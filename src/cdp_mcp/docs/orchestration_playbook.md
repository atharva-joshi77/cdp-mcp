# CDP Orchestration Playbook

Authoritative recipes for multi-step orchestration flows that the single-tool MCP calls cannot cover on their own. Every recipe here was reverse-engineered from `ui-vega` / `ui-config` (`2601-release`) services — specifically `ConnectorDataService`, `ScheduleService`, `ReportDataService`, `dataExport.service.ts`, and `provisioner.service.js`.

Exposed as MCP resource `cdp://docs/orchestration-playbook`.

## 0. The universal pattern

Almost every "do this thing periodically / on-demand" feature in CDP is built from three primitives:

1. A **definition row** (campaignDef, reportDef, exportDef, connector, …).
2. A **schedule row** in `config/schedules` that references a **runner workflow** (`AIF_RUNNER`, `REPORT_RUNNNER_DEFAULT`, `DATA_EXPORT_DEFAULT`, `CAMPAIGN_FLOW_DEFAULT`, `CONNECTOR_OPS_DEFAULT`, `PROVISIONER_TOOL_DEFAULT`).
3. A **workflow action invocation** (`POST config/workflows/{name}?action=<verb>&entityType=…&entityId=…&scheduleId=…`) that the UI fires *in addition to* writing the schedule row.

If you only do step 2 (POST `/config/schedules`), the schedule appears in the list view but the runner never fires. **You must also invoke the schedule/unschedule action on the runner workflow.** Use `cdp_invoke_workflow_action`.

## 1. Generic schedule lifecycle

Canonical verbs per entity type:

| entityType  | runner workflow           | schedule verb | unschedule verb | run verb (one-off) |
|-------------|---------------------------|---------------|-----------------|--------------------|
| connector   | `AIF_RUNNER`              | schedule      | unschedule      | (n/a — use `CONNECTOR_OPS_DEFAULT` action=publish) |
| report      | `REPORT_RUNNNER_DEFAULT`  | schedule      | unschedule      | run (`{"reportProperties":"{}"}`) |
| exportDef   | `DATA_EXPORT_DEFAULT`     | schedule      | unschedule      | run (`{"dataExportProperties":"{}"}`) |
| campaign    | `CAMPAIGN_FLOW_DEFAULT`   | schedule      | unschedule      | run (`{"campaignProperties":"{}"}`) |
| provisioner | `PROVISIONER_TOOL_DEFAULT`| n/a           | n/a             | run (instance body) |

### 1.1 Create a schedule (generic)

```text
# 1. Look up the runner workflow to get its numeric DB id.
wf = cdp_get_workflow(workflow_id="REPORT_RUNNNER_DEFAULT")
reference_id = wf["id"]            # numeric, NOT the name

# 2. Create the schedule row.
body = {
  "type": "WORKFLOW",
  "referenceId": reference_id,
  "entityType": "report",
  "entityId": <reportDef.resourceId>,
  "scheduleName": "Schedule-<16-char-random>",
  "active": true,
  "period": "DAYS",
  "frequency": 1,
  "startTime": "00:00",
  "startTimestamp": "2026-05-01T09:00",
  "timeZone": "America/New_York",
  "jobData": {"reportProperties": "{}"}
}
sched = cdp_create_schedule(body=json.dumps(body))

# 3. Arm the schedule on the runner workflow.
cdp_invoke_workflow_action(
  workflow_id="REPORT_RUNNNER_DEFAULT",
  action="schedule",
  entity_type="report",
  entity_id=reportDef.resourceId,
  schedule_id=sched["scheduleId"],
)
```

### 1.2 Update a schedule

```text
cdp_update_schedule(schedule_id=<id>, body=json.dumps({... full body ...}))
```
Pass the same `referenceId`/`entityType`/`entityId` or CDP detaches the schedule.

### 1.3 Delete a schedule (UI-correct order)

```text
# 1. Detach from runner workflow FIRST.
cdp_invoke_workflow_action(
  workflow_id="AIF_RUNNER",
  action="unschedule",
  entity_type="connector",
  entity_id=<connectorId>,
  schedule_id=<scheduleId>,
)

# 2. Then delete the row.
cdp_delete_schedule(schedule_id=<scheduleId>)
```

Doing only step 2 leaves dangling trigger registrations in some runners (confirmed in `ConnectorDataService.deleteSchedule`).

### 1.4 Activate / deactivate (non-destructive toggle)

```text
cdp_deactivate_schedule(workflow_id="REPORT_RUNNNER_DEFAULT", schedule_id=<id>)
cdp_activate_schedule  (workflow_id="REPORT_RUNNNER_DEFAULT", schedule_id=<id>)
```
These emit `action=activate_schedule` / `deactivate_schedule`. They do NOT affect the schedule row — only the runner's in-memory trigger.

## 2. Connector lifecycle

Source: `ui-core/src/app/services/connector/connector.service.js`.

### 2.1 Create → publish

```text
conn = cdp_create_connector(body=json.dumps({...}))
cdp_invoke_workflow_action(
  workflow_id="CONNECTOR_OPS_DEFAULT",
  action="publish",
  entity_type="connector",
  entity_id=conn["resourceId"],
)
```
"Publish" writes the connector to the runner's catalogue; without it the connector exists but the ingest pipeline doesn't know about it.

### 2.2 Schedule a published connector

Exactly the recipe in §1.1 but with `entity_type="connector"`, runner `AIF_RUNNER`, and `jobData` omitted (AIF_RUNNER reads the connector row itself).

### 2.3 Get execution history

```text
GET config/connectors/{id}/history   (use cdp_get_connector_history if available,
                                      or raw: cdp_http_get — but this MCP exposes
                                      cdp_get_connector_versions for definition
                                      versions, not runtime history; see §9)
```
Execution summary: `GET config/connectors/{id}/summary`.

### 2.4 Unschedule / delete

Follow §1.3 with `workflow_id="AIF_RUNNER"`, then `cdp_delete_connector`.

## 3. Report lifecycle

Source: `ui-vega/src/app/main/reports/report-data.service.ts`.

### 3.1 Save a report (folderId-aware, PUT vs POST)

```text
# Update existing report
cdp_update_report_def(report_id=..., folder_id=<id>, body=json.dumps(reportDef))

# Create new report
cdp_create_report_def(folder_id=<id>, body=json.dumps([reportDef]))
# NOTE the outer array — the Campaign API POST expects a LIST.
```
`folderId` must be sent even for root (`folderId=0`); missing it causes silent "uncategorised" placement.

### 3.2 Send report now (one-off)

```text
cdp_run_workflow(
  workflow_id="REPORT_RUNNNER_DEFAULT",
  entity_type="report",
  entity_id=<reportDef.resourceId>,
  body=json.dumps({"reportProperties": "{}"}),
)
```

### 3.3 Schedule recurring report

§1.1 with `entity_type="report"`, runner `REPORT_RUNNNER_DEFAULT`, `jobData={"reportProperties":"{}"}`.

### 3.4 Fetch the last executed dataset

```text
GET dw/report/reportDefs/{id}?action=fetch
```
Use `cdp_fetch_report_data` (or an equivalent DW report tool). For multi-report dashboards, call it N times and concatenate `data.dataset` (per `getMultiReportData` in ui-vega); attribute sets must match across reports or the merge is rejected.

## 4. Data export lifecycle

Same shape as reports, with runner `DATA_EXPORT_DEFAULT` and body key `dataExportProperties`. The complete flow is already covered by `cdp_list_data_exports`, `cdp_create_data_export`, `cdp_update_data_export`, `cdp_copy_data_export`, `cdp_run_data_export`. Scheduling uses §1.1.

## 5. sQueryDef preview-before-save

Source: `ui-config/src/app/main/squery-templates/squery-templates.data.service.js`.

When a user writes or imports a query template, the UI ALWAYS runs generate + validate before save:

```text
args = cdp_generate_squery_def(body=json.dumps({expression, arguments, ...}))
ok   = cdp_validate_squery_def(body=json.dumps({expression, arguments: args, ...}))
if ok.success:
    cdp_create_squery_def(body=json.dumps({...populated with generated args...}))
```
Skipping `generate` → `validate` will pass lint but fail at run-time when the engine cannot bind arguments. Reliable pattern: treat `generate` output as the source of truth for `arguments` / `outputAttributes`.

## 6. sQueryDef templating (reusing a saved template by name)

```text
templates = cdp_list_campaign_templates(type="SQUERY",
                                        fields='["createdBy","createdDate","editedDate","Version","active"]')
template  = next(t for t in templates if t.name == "my-query")
# Use template.content to seed the new def, then run §5.
```

## 7. Provisioning (run a service package)

Source: `ui-config/src/app/main/provisioner/provisioner.service.js`.

```text
packages = cdp_list_provision_services()              # GET provisioning/packages
payload  = {... package config ...}
cdp_invoke_workflow_action(
  workflow_id="PROVISIONER_TOOL_DEFAULT",
  action="run",
  body=json.dumps(payload),
)
# Then poll cdp_list_provision_instances or cdp_get_provision_instance until
# status ∈ {PROVISIONED, FAILED}.
```
`PROVISIONER_TOOL_DEFAULT` is synchronous enough to return an `instanceId` but the actual infra is async — always poll.

## 8. Compaction request

Source: `ui-config/src/app/main/compaction/compaction.service.js`.

```text
cdp_create_compaction_request(body=json.dumps({
  "udmpTable": "customer",
  "priority": "HIGH",          # UI force-sets HIGH on create
  ... other fields ...
}))

# Cancel a pending one
cdp_unschedule_compaction_request(id=<reqId>)
# (internally: POST compactionRequests/{id}?action=unschedule)
```

## 9. Status / job control

`cdp_get_workflow_job` / `cdp_rerun_job` / `cdp_kill_job` / `cdp_suspend_job` / `cdp_resume_job` wrap the `POST config/workflows/{workflowName}?action=<verb>&jobId=...&entityId=...&entityType=...` pattern the UI fires from the Status page (`ui-config/src/app/main/status/status.controller.js`).

Canonical sequence when a job is stuck:
```text
1. cdp_get_workflow_job(workflow_id, job_id)
2. if stuck ≥ 30 min → cdp_suspend_job(workflow_id, job_id)
3. investigate (logs / datasetDescriptions/executionEngine)
4. cdp_resume_job   OR   cdp_kill_job + cdp_rerun_job(job_id)
```

## 10. Batch updates (rules / resources)

Sources: `A360RuleDataService.saveResources`, `DQERulesDataService.updateRules`.

Both services accept a tuple `(creates, updates, deletes)` and fan out to REST with `vegaHttp.all(requests)`. The MCP does NOT have a batch endpoint — do this client-side:

```text
for item in creates:
    cdp_create_a360_rule(body=json.dumps(item))
for item in updates:
    cdp_update_a360_rule(rule_id=item.id, body=json.dumps(item))
for rid in deletes:
    cdp_delete_a360_rule(rule_id=rid)
```
Do **creates first**, then updates, then deletes — to avoid FK constraint errors when a new rule references an existing column that a concurrent delete removes.

Same pattern for `dqe1Rules` / `dqe2Rules`.

## 11. Customer-360 identity purge (GDPR)

Source: `customer360.service.ts::purgeIdentities` and `DataErasureController`.

```text
cdp_request_data_erasure(body=json.dumps({
  "customerIds": ["KFK_0_user@example.com"],
  "reason": "GDPR right to erasure",
  "requester": "<user email>"
}))
# Returns an erasureId. Poll:
cdp_get_data_erasure_status_by_id(erasure_id=<id>)
# until status ∈ {COMPLETED, FAILED}.
```
The UI sets `httpConfig.skipErrorMessage = true` on the POST — replicate by being tolerant of 202/404 during the first few seconds while the async worker registers the request.

## 12. Content model / template provisioning

Source: `ui-config/src/app/main/content-models/content-models.service.js`.

```text
# Read ALL template versions (UI uses a fetchAll endpoint that bypasses tenant scoping)
cdp_list_campaign_templates(type="EMAIL", mode="fetchAll")

# Provision/update a set of templates atomically
PUT campaign/templates/provision?action=update   body=[{...}, {...}]
```
No dedicated MCP tool for the `action=update` provisioning yet — invoke via the raw http client or open an enhancement ticket.

## 13. Reusable helper mental model

When the MCP is missing a one-call wrapper, ALWAYS break the action into:

```
(a) fetch runner workflow id             cdp_get_workflow
(b) POST the definition / schedule row   cdp_create_* / cdp_update_*
(c) POST the workflow action verb        cdp_invoke_workflow_action
(d) poll status                          cdp_get_workflow_job / cdp_get_status
```

Every complex orchestration in the Vega/Config UI decomposes into exactly that sequence.

