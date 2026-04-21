# Workflow Authoring Playbook

Authoritative flow for authoring, modifying, deploying, and invoking CDP
`configAPI` workflows — derived from
`ui-core/src/app/services/workflow/workflow.service.js` and
`ui-config/src/app/main/workflow/workflow.controller.js`.

A workflow in CDP is a **graph**: a top-level `workflows/{id}` row plus two
sub-collections (`workflowSteps`, `workflowEdges`) that can be versioned
independently. This playbook covers the sequencing that atomic MCP tools
cannot encode on their own.

---

## 1. The `workflowId` vs `workflowEntityId` trap

Every workflow has **two identifiers**:

| Name | Type | Example | Where used |
|------|------|---------|------------|
| `workflowId` (symbolic) | string | `"AIF_RUNNER"`, `"CAMPAIGN_FLOW_DEFAULT"`, `"DATA_EXPORT_DEFAULT"` | **URL segment** `workflows/{workflowId}` |
| `workflowDBId` / `id` (numeric) | integer | `42`, `108` | **Query param** `entityId=<n>` when you invoke the workflow against an *entity* |

The UI helper `invokeWorkflowForSchedule(scheduleId, workflowId, workflowDBId, action, data, version)`
sends both. Example rendering:

```
POST /v2/{tid}/config/workflows/AIF_RUNNER
   ?entityType=workflow
   &entityId=42            ← workflowDBId, not AIF_RUNNER
   &action=schedule
   &scheduleId=88
   &version=3
```

**Common failure**: passing `"AIF_RUNNER"` as `entityId`. The server 500s with
a number-parse error that looks like a transient DB issue.

Rules:

- `workflows/<URL>` segment → symbolic name (or numeric workflowId for
  user-authored workflows).
- `entityId` query param → **numeric DB id** from `GET workflows/{name}` →
  `response.data.id`.
- Cache `response.data.id` after the first GET; it never changes for system
  workflows.

The MCP tool `cdp_invoke_workflow_action` takes `workflow_name` (symbolic) and
`entity_id` (numeric) separately — do not conflate them.

---

## 2. Loading a full workflow = 3 parallel GETs

A single `GET workflows/{id}` returns only the root row. To materialize a
workflow graph for inspection or editing you must fetch three resources in
parallel:

```
parallel:
    GET workflows/{id}[?version=<v>]              → workflow row
    GET workflows/{id}/workflowSteps[?version=<v>] → paged list
    GET workflows/{id}/workflowEdges[?version=<v>] → paged list
```

Then assemble:

```python
workflow = responses[0]["data"]
workflow["steps"] = responses[1]["data"]["content"]
workflow["edges"] = responses[2]["data"]["content"]
```

Notes:

- Paginate `workflowSteps` and `workflowEdges` at `limit=500` (UI default).
- If `version` is passed, it must be applied to **all three** requests. A
  mismatch returns inconsistent partial graphs silently.
- The MCP has atomic tools for each of the three; callers should issue them
  concurrently and merge client-side.

---

## 3. Versioning: query-string only on deploy/delete

Versioning semantics that repeatedly trip up integrators:

| Operation | Version location |
|-----------|------------------|
| `GET workflows/{id}` and sub-collections | **Query param** `?version=<v>` |
| `PUT workflows/{id}` (update) | **Not allowed** — PUT always writes to the current draft. |
| `POST workflows/{id}?action=deploy&version=<v>` | Query param — deploys the *stated* version. |
| `DELETE workflows/{id}?version=<v>` | Query param — deletes a specific version; omit to delete the whole workflow. |

**Do not** put `version` in the body. The controller silently ignores it and
you'll think your change landed on v4 when in fact it landed on the current
draft.

---

## 4. Step authoring: batch POST / batch PUT (not per-step)

Unlike mapping scripts (see §5), workflow steps are saved with **one
POST for all new steps** and **one PUT for all updated steps**:

```
POST workflows/{id}/workflowSteps   body: [newStep1, newStep2, ...]
PUT  workflows/{id}/workflowSteps   body: [updatedStep1, updatedStep2, ...]
```

The path is identical for both; the backend discriminates by HTTP method.
Sending a `PUT` with an array containing items missing `id` fields is rejected
with a cryptic 409 — every item in the PUT array **must** have its existing
step `id`.

### Edges

Edges are saved as a single replacement:

```
POST workflows/{id}/workflowEdges   body: [edge, edge, ...]
```

This POST replaces the entire edge set. There is no PUT and no per-edge
endpoint — if you want to keep existing edges, include them all. Missing an
edge on POST is equivalent to deletion.

---

## 5. Mapping scripts: per-record POST/PUT/DELETE in parallel

Mapping scripts (code executed inside a step) follow the opposite convention
— one request per script, fanned out in parallel:

```
parallel:
  POST   workflows/{w}/workflowSteps/{s}/mappingScripts       body: newScript1
  POST   workflows/{w}/workflowSteps/{s}/mappingScripts       body: newScript2
  PUT    workflows/{w}/workflowSteps/{s}/mappingScripts/{id}  body: updatedScript
  DELETE workflows/{w}/workflowSteps/{s}/mappingScripts/{id}
```

The UI `saveMappingScripts(workflowId, stepId, create[], update[], delete[])`
wraps this in a single `vegaHttp.all(requests)` call. MCP consumers must issue
these N requests themselves; there is no bulk endpoint.

Atomic tool: if only `cdp_create_mapping_script` / `cdp_update_mapping_script`
/ `cdp_delete_mapping_script` are available, issue them concurrently. A
failure in one does **not** roll back the others — the UI treats this as
best-effort and shows partial errors.

---

## 6. The create → deploy sequence for a new workflow

```
1. POST workflows                                 body: {workflowId: "MY_WF", ...}
2. parallel:
     PUT workflows/MY_WF                          body: {...metadata...}   # only if you need to add fields
     POST workflows/MY_WF/workflowSteps           body: [step, step, ...]
3. POST workflows/MY_WF/workflowEdges             body: [edge, edge, ...]
4. POST workflows/MY_WF?action=deploy             (no body; version defaults to latest)
```

Only after step 4 is the workflow runnable. Sending `action=run` on an
undeployed workflow returns 409.

---

## 7. Invocation verbs (`workflows/{id}?action=<verb>`)

A non-exhaustive list of action verbs observed across the Vega / Config UIs:

| Verb | Context | Required query/body |
|------|---------|---------------------|
| `run` | Immediate execution against an entity | `entityType=<t>&entityId=<n>` + body wrapper `{"<t>Properties":"{}"}` (e.g. `campaignProperties`, `reportProperties`, `dataExportProperties`) |
| `deploy` | Deploy new/updated workflow | `version=<v>` (optional, defaults to latest draft) |
| `schedule` | Arm a runner workflow (AIF_RUNNER) against a schedule row | `entityType=<t>&entityId=<n>&scheduleId=<sid>` |
| `unschedule` | Disarm runner workflow before deleting the schedule row | same as `schedule` |
| `activate_schedule` / `deactivate_schedule` | Enable/disable a schedule without deletion | `scheduleId=<sid>` |
| `rerun` | Rerun a failed job (StatusController invokes this) | `jobId=<jid>` (see orchestration playbook) |
| `kill` | Cancel a running job | `jobId=<jid>` |
| `publish` | Publish a connector (CONNECTOR_OPS_DEFAULT) | `entityType=connector&entityId=<cid>` |
| `update` | Templates provision bulk update | body = update payload; see `PUT templates/provision?action=update` |

The MCP generic `cdp_invoke_workflow_action` accepts `workflow_name`,
`action`, and arbitrary `params`/`body`. It is the right tool when a
specialized wrapper doesn't exist.

---

## 8. Deleting a workflow safely

Before calling `DELETE workflows/{id}`, drain everything that references it:

1. **Any running job** for this workflow — kill via
   `cdp_invoke_workflow_action(workflow_name="<SYS>", action="kill", params={"jobId": <jid>})`.
2. **Any schedule** with `referenceId == workflowDBId` — unschedule then
   delete via `cdp_delete_schedule` (see orchestration playbook §1.3).
3. Only then call `cdp_delete_workflow(id, version?)`. Omitting `version`
   deletes **all** versions; passing it deletes a single version and retains
   the rest.

Skipping (1) orphans a running job that keeps holding cluster resources;
skipping (2) orphans a schedule row whose runner now points at a deleted
workflow (the scheduler will throw every cycle until the row is manually
removed).

---

## 9. System workflows you will encounter

| Symbolic name | Used for |
|---------------|----------|
| `AIF_RUNNER` | Generic schedule runner; arms any entity against a schedule row |
| `AIF_TENANT_PROVISIONER` | Provisioning packages at tenant level |
| `CONNECTOR_OPS_DEFAULT` | Connector lifecycle actions (`publish`, `unpublish`) |
| `CAMPAIGN_FLOW_DEFAULT` | Campaign start/stop/publish (web and batch) |
| `REPORT_RUNNNER_DEFAULT` | Report send-now and scheduled runs (**triple N**) |
| `DATA_EXPORT_DEFAULT` | Data-export send-now and scheduled runs |
| `PROVISIONER_TOOL_DEFAULT` | Cross-tenant provisioning — invoked with templated URL |
| `BI_MAPPER_DEFAULT` | BI data mapping (cube freshness signal) |
| `A1_ORCHESTRATOR` | Top-level BI orchestration wrapper |

All require the `entityType` + `entityId` (numeric DB id) pair on `action=run`
except `AIF_RUNNER` which also needs `scheduleId`.

---

## 10. Failure modes you will hit

- **409 "workflow not deployed"** — forgot `action=deploy` after step/edge
  authoring.
- **500 "number format exception"** — passed symbolic `workflowId` as
  `entityId`. Use the numeric DB id.
- **PUT steps silently appends instead of updating** — you included a `version`
  field in the body. The server routes based on method + whether each item has
  an `id`; any `version` key must live in the URL query string.
- **Deploy returns "no draft"** — you tried to deploy a workflow whose current
  version is already live and unchanged. Edit something (even metadata) first.
- **Edges disappeared after save** — the POST edges call replaces the entire
  set. Include all edges you want to keep.

