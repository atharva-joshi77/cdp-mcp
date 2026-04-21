# CDP Admin Ops Playbook

Recipes for administrative / data-governance workflows that require multiple MCP calls in a specific order. Reverse-engineered from the `ui-config` (`2601-release`) app — specifically DQE, A360 rules, compaction, status, data-erasure, and content-model services.

Exposed as MCP resource `cdp://docs/admin-ops-playbook`.

## 1. DQE rule batches

Source: `ui-config/src/app/main/dqe/dqe-data.service.js`.

DQE has two tiers:
- **DQE1** — hard rules (reject the record). `dqe1Rules` endpoint.
- **DQE2** — soft rules (flag but keep). `dqe2Rules` endpoint.

### 1.1 Authoring pattern

```text
# Fetch once, mutate client-side, save in tiers.
rules1 = cdp_list_dqe1_rules()
rules2 = cdp_list_dqe2_rules()

# compute creates / updates / deletes locally
for r in creates1:  cdp_create_dqe_rule(is_dqe1=True, body=json.dumps(r))
for r in updates1:  cdp_update_dqe_rule(is_dqe1=True, rule_id=r.ruleId, body=json.dumps(r))
for rid in deletes1: cdp_delete_dqe_rule(is_dqe1=True, rule_id=rid)
# repeat for DQE2
```

**Order matters:** creates first, then updates, then deletes. The backend enforces that referenced columns exist at rule-evaluation time.

### 1.2 Preview before save

DQE rules have no `validate` endpoint, unlike sQueryDefs. The authoring UI runs a dry execution by creating the rule `active=false`, running a single compaction cycle against the staging dataset, then toggling `active=true`. Agents should replicate this when adding rules that could break ingest:

```text
1. cdp_create_dqe_rule(body=json.dumps({..., "active": false}))
2. cdp_create_compaction_request(body=json.dumps({
     "udmpTable": rule.tableName,
     "priority": "HIGH"}))
3. cdp_list_compaction_requests(active=true)   # poll until done
4. cdp_update_dqe_rule(rule_id=..., body=json.dumps({..., "active": true}))
```

## 2. A360 rule administration

Source: `ui-config/src/app/main/360/customer360-data.service.js`.

### 2.1 Save in three phases

```text
# Phase 1: new rules
for r in creates: cdp_create_a360_rule(body=json.dumps(r))
# Phase 2: modified rules
for r in updates: cdp_update_a360_rule(rule_id=r.id, body=json.dumps(r))
# Phase 3: deletes (LAST — maintain FK integrity for columns)
for rid in deletes: cdp_delete_a360_rule(rule_id=rid)
```

### 2.2 Column-level update

Individual column PUT is exposed by `A360RuleDataService.updateColumn`:
```text
PUT config/a360Rules/columns/{columnId}   body = column object
```
Used when the UI edits one cell in the rule grid without re-saving the whole rule. If your MCP doesn't expose a dedicated tool, fall back to updating the parent rule with the modified column inline.

### 2.3 Validate before deploy

Always run `§8 Layout validation` from the Customer 360 playbook BEFORE deleting any rule that contributes `customizationColumns`. Deleting a rule that's referenced by the merged layout produces empty cells at runtime.

## 3. Compaction lifecycle

Source: `ui-config/src/app/main/compaction/compaction.service.js`.

### 3.1 Canonical request

```text
cdp_create_compaction_request(body=json.dumps({
  "udmpTable": "<tableName>",
  "priority": "HIGH",     # UI force-sets HIGH
  # optional: "scheduledAt", "userComment", ...
}))
```
The UI overrides `priority` to `HIGH` unconditionally — replicate unless you deliberately want background compaction.

### 3.2 Cancel

```text
cdp_unschedule_compaction_request(id=<reqId>)
# internally: POST compactionRequests/{id}?action=unschedule
```

### 3.3 Check state

```text
# All open:
cdp_list_compaction_requests(active=true)
# Historical (including completed/failed):
cdp_list_compaction_requests(active=false)
```

## 4. Status page / job control

Source: `ui-config/src/app/main/status/status.controller.js`.

The UI calls a generic `POST config/workflows/{workflowName}?action=<verb>&jobId=<id>&entityId=<eid>&entityType=<etype>`. Verb map (from `entityTypeMap` in the controller):

| workflowName            | entityType |
|-------------------------|------------|
| CAMPAIGN_FLOW_DEFAULT   | campaign   |
| REPORT_RUNNNER_DEFAULT  | report     |
| DATA_EXPORT_DEFAULT     | exportDef  |
| AIF_RUNNER              | connector  |
| PROVISIONER_TOOL_DEFAULT| service    |

### 4.1 Rerun a failed job

```text
cdp_rerun_job(workflow_id="CAMPAIGN_FLOW_DEFAULT",
              job_id=<jobId>,
              entity_type="campaign",
              entity_id=<campaignId>)
```
(or drop to `cdp_invoke_workflow_action(action="rerun", ...)` when the dedicated tool is missing.)

### 4.2 Kill + rerun pattern (safest for stuck jobs)

```text
cdp_kill_job(workflow_id=..., job_id=...)
cdp_get_workflow_job(workflow_id=..., job_id=...)   # confirm KILLED
cdp_rerun_job(workflow_id=..., job_id=...)          # new jobId issued
```

### 4.3 Fetch execution-engine icon/state

```text
GET config/datasetDescriptions/executionEngine?defId=<eid>&defType=<type>&key=<jobId>
```
Signals whether the job ran on Spark / BigQuery / Snowflake. The MCP currently exposes this via raw HTTP — agents should add `cdp_get_execution_engine` if the need is frequent.

### 4.4 Status filtering parameters

The list page filters by `selectedDay` OR `(fromDate, toDate)` — mutually exclusive. When both are set, `selectedDay` wins. Replicate server-side:
```text
cdp_list_status(
  days=7,                          # preferred
  # OR
  from_date="2026-04-01",
  to_date="2026-04-20",
)
```

## 5. Purge / data-erasure flow (GDPR)

Source: `customer360.service.ts::purgeIdentities` + `DataErasureController`.

### 5.1 Request erasure

```text
cdp_request_data_erasure(body=json.dumps({
  "customerIds": [...],
  "reason": "GDPR right to erasure",
  "requester": "<agent email>"
}))
```
Response contains `erasureId`.

### 5.2 Poll status

```text
cdp_get_data_erasure_status_by_id(erasure_id=<id>)
# → {status: PENDING|RUNNING|COMPLETED|FAILED, steps: [...]}
```

### 5.3 Override / update status (ops only)

```text
cdp_data_erasure_status_override(erasure_id=<id>, body=json.dumps({...}))
```
Use when a stuck erasure needs a manual force-complete — the UI surfaces this through a dialog for admin users only.

### 5.4 Purge statuses (different controller)

Separate read endpoint for purge history across erasure + compaction:
```text
GET dw/purge?limit=&offset=
```
Exposed as `cdp_list_purge_records`.

## 6. Provisioner workflow

Source: `provisioner.service.js`.

### 6.1 List packages

```text
cdp_list_provision_packages()    # GET provisioning/packages (cached)
```

### 6.2 Run

```text
cdp_invoke_workflow_action(
  workflow_id="PROVISIONER_TOOL_DEFAULT",
  action="run",
  body=json.dumps({... package + instance config ...}),
)
```

The response contains the new `provisionInstanceId`. Poll:

```text
cdp_get_provision_instance(instance_id=...)
# status ∈ {PENDING, PROVISIONING, PROVISIONED, FAILED, DEPROVISIONING, DEPROVISIONED}
```

### 6.3 Lifecycle actions

Use the dedicated tools — they map to `provisions/instances/{id}?action=<verb>`:

| Action        | Tool                                 |
|---------------|--------------------------------------|
| Deactivate    | `cdp_deactivate_provision_instance`  |
| Deprovision   | `cdp_deprovision_instance`           |
| Retry         | `cdp_retry_provision_instance`       |
| Reactivate    | `cdp_reactivate_provision_instance`  |

## 7. Content-model template provisioning

Source: `ui-config/src/app/main/content-models/content-models.service.js`.

### 7.1 Read (bypass tenant scoping with `fetchAll`)

```text
# Superset of templates, across tenants the user has access to
cdp_list_campaign_templates(type="EMAIL", mode="fetchAll", offset=0, limit=500)

# Tenant-scoped slice with subset of fields
cdp_list_campaign_templates(type="EMAIL",
                            fields='["properties"]',
                            offset=0, limit=500)
```

### 7.2 Bulk provision/update

```text
PUT campaign/templates/provision?action=update
body = [ {templateObj}, {templateObj}, ... ]
```
No dedicated MCP wrapper yet — file an enhancement or call via raw HTTP. The endpoint is atomic: either all templates update or none do.

## 8. User / role provisioning

Source: `ui-config/src/app/main/user`.

Sequence when onboarding a new user with a custom role:

```text
1. cdp_create_role(body=json.dumps({name, permissions:[...]}))       # or self-service
2. cdp_create_user(body=json.dumps({email, roles:[roleId], ...}))
3. cdp_invite_user(user_id=...)     # if the UI surfaces an invite endpoint
```
Reverse order for decommission: remove user → remove role.

Permissions follow the `<service>:<resource>` pattern (e.g. `configapi:connectors`). Verbs: `read, write, update, delete, generate, validate, publish`. The UI checks with `vegaUser.hasPermissions('<key>', ['write','update'], 'rest')`.

## 9. Mapping templates

Source: `mapping-templates-data.service.js`. Plain CRUD on `config/mappingTemplates` — no orchestration. Use `cdp_list_mapping_templates`, `cdp_create_mapping_template`, `cdp_update_mapping_template`, `cdp_delete_mapping_template`.

Only gotcha: the UI **always** reloads the full list after a mutation (no partial update) — safe to assume optimistic updates are not server-supported. Re-fetch after writes.

## 10. Cluster / tenantCluster management

Source: UI has a limited surface; most admin work happens via CDP Platform Orchestration. Via MCP:

- `cdp_list_clusters` → compute clusters available to the tenant.
- `cdp_list_tenant_clusters` (if wired) → tenant-to-cluster mappings.

No UI orchestration beyond list/read — this is read-only for in-app agents.

## 11. Universal "drain-before-delete" rule

Whenever deleting a parent entity that owns schedules, jobs, or runner registrations, follow this strict order:

1. `cdp_list_schedules(entity_type=..., entity_id=...)` → find attached schedules.
2. For each: `cdp_invoke_workflow_action(action="unschedule", ...)` then `cdp_delete_schedule`.
3. `cdp_get_workflow_job` on each active job → kill if running.
4. Finally `cdp_delete_<entity>`.

Skipping (1) or (2) creates orphan trigger registrations that re-create defunct job rows on the next runner tick.

