# Reports & Dashboards Playbook

Authoritative flow for creating, saving, executing, and scheduling report
definitions, cube (OLAP) reports, SQL-query reports, and dashboards — derived
from `ui-vega/src/app/main/reports/**` (`report-data.service.ts`,
`cube-data.service.ts`, `sql-report.data.service.ts`) and
`ui-vega/src/app/main/dashboard/services/dashboard.service.ts`.

The MCP exposes atomic tools per endpoint. This playbook documents the sequencing
and body contracts that an LLM using those tools will otherwise get wrong.

---

## 1. Non-obvious body / verb contracts

| Operation | Tool | Gotcha |
|-----------|------|--------|
| Create report | `cdp_create_report_def` | **Body must be wrapped in a JSON array**: `[reportDef]`. Response comes back as `response.data.content[0]`. |
| Update report | `cdp_update_report_def` | Plain object (not array). URL must include `?folderId=<id>` on save/update — the server uses this to assign the report to a folder. If omitted the report lands in the root folder and becomes hard to locate. |
| Create dashboard | `cdp_create_dashboard` | **Body is `[dashboard]` array**, same convention as reports. Response is `content[0]`. |
| Dashboard layout | `cdp_create_dashboard` / `cdp_update_dashboard` | `layout` is **not stored directly** — stringify to JSON and put it in `uiProperties` as `{"cells": <layout>, "viewportHeight": h, "viewportWidth": w}`. On read, parse `uiProperties` back out. |
| Send-now (run) report | `cdp_run_workflow` with `workflow_name="REPORT_RUNNNER_DEFAULT"` | **Note the triple-N typo** — `RUNNNER`, not `RUNNER`. This is the real backend name. Body `{"reportProperties":"{}"}`, query params `action=run&entityType=report&entityId=<resourceId>`. |
| Execute cube ad-hoc | `cdp_execute_report` (`dw/report/reportDefs?action=execute`) | Body: `{"name":"Cube Report","reportType":"CUBIC_SET","realtime":true,"cubicSetDef":{"name":"Cube Data","model":"<stringified JSON>"}}`. `cubicSetDef.model` **must be a JSON string**, not an object. |
| Fetch cached cube/SQL result | `cdp_fetch_report_data` (`dw/report/reportDefs/{id}?action=fetch`) | Returns last executed dataset; do not confuse with `action=execute`. |
| Cube status by name | `cdp_get_cube_status` | Query is `cubeStatus?cubes=["<name>"]` — the parameter is a URL-encoded JSON array even when checking a single cube. |

> Rule: treat `POST reportDefs` and `POST dashboards` as **bulk** endpoints that
> happen to be used for one-at-a-time UI saves. Forgetting the array wrap
> produces a 400 with a confusing "content is missing" error.

---

## 2. Save → schedule → send-now lifecycle

The UI gates each stage on dirty-checks. For MCP consumers, the same three
transitions must be sequenced in order:

1. **Save / update definition.** Compute dirty state yourself (or call
   `cdp_get_report_def` and diff). PUT if `resourceId` exists, otherwise POST
   with `[reportDef]` array wrap. Always attach `?folderId=`.
2. **Save the schedule** (if enabled).
   Schedule lifecycle is documented in the orchestration playbook. For reports
   the `workflow` is `REPORT_RUNNNER_DEFAULT` and the body wrapper is
   `{"reportProperties":"{}"}`.
3. **Send-now** (if user requested immediate execution).
   Same workflow, `action=run`, `entityType=report`, `entityId=<resourceId>`.
   Poll status via `cdp_list_orchestration_statuses` keyed on the returned
   `scheduleId` or via `StatusDataService.getLastRunStatus("REPORT_RUNNNER_DEFAULT")`.

**Do not** attempt send-now before the save has returned a `resourceId`.
The UI rejects this client-side and the backend has no resolver for the
pending object.

---

## 3. Dashboard composition

Dashboards in `reportAPI` are thin containers — they hold `widgetDefs` which
reference `reportDefs` by `resourceId`. A single dashboard fetch (`GET
dashboards/{id}`) returns:

- the dashboard row itself (`uiProperties` still a JSON string)
- `widgetDefs[]` with each widget's `reportDefs: [{reportType, resourceId}]`

The UI then performs an **N+1 fetch** to materialize each widget's report:

```
for cell in layout.cells:
    if cell.chartOptions.reportId and not array:
        GET reportDefs/{reportId}       # per-widget
```

LLMs replicating the UI should:

1. Call `cdp_get_dashboard(id)`.
2. Parse `uiProperties` as JSON to extract `cells`.
3. Optionally call `cdp_get_report_def` for each unique `reportId` in
   parallel — these are independent and can be batched.

### Save path

- POST → `dashboards?folderId=<fid>` body `[dashboard]`.
- PUT → `dashboards/{id}?folderId=<fid>` body `dashboard`.
- Always serialize `{cells, viewportHeight, viewportWidth}` into
  `uiProperties` before POST/PUT. Strip the in-memory `layout` key.
- `widgetDefs` stay in the dashboard body — do not try to persist them
  separately.

---

## 4. Cube (OLAP) reporting

The cube flow uses `reportAPI` for metadata and `dwAPI` for execution.

### 4.1 Metadata walk

```
GET report/cubemetadata            → list of catalogs
for each cube in flatten(catalogs.schemas.cubes):
    GET report/cubemetadata/{cubeName}   → dimensions + measures + properties
```

All cube names must be `encodeURIComponent(name)` — many cubes contain spaces
or special characters. The MCP HTTP client already URL-encodes, but raw
path strings built by the caller will not.

### 4.2 Drill-down

```
GET report/cubemetadata/{cube}/dimensions/{dim}/hierarchies/{hier}/levels/{lvl}
```

Every segment is URL-encoded independently. The response body uses `result`
as a JSON-string wrapper — parse it before consuming.

### 4.3 Ad-hoc query (realtime, un-saved)

```
POST dwAPI report/reportDefs?action=execute
body: {
  "name": "Cube Report",
  "reportType": "CUBIC_SET",
  "realtime": true,
  "cubicSetDef": { "name": "Cube Data", "model": "<JSON-stringified MDX model>" }
}
```

Response shape: `response.data.dataset[0].result` holds the actual tuples. The
`cubicSetDef.model` field is a **stringified JSON payload**, not a nested
object.

### 4.4 Saved-query fetch

```
GET dwAPI report/reportDefs/{id}?action=fetch
```

Returns last materialized dataset for saved cube or SQL reports. Use this
instead of `?action=execute` when you want cached results.

### 4.5 Cube freshness status

```
GET reportAPI cubeStatus?cubes=["<name>"]
```

- Single cube: still pass a JSON array of one name.
- Omit the query string for all-cubes status.

### 4.6 BI-workflow readiness (dual check)

Before running a cube report, verify that BI data is fresh. The UI watches
**both** workflows and picks whichever finished last:

- `BI_MAPPER_DEFAULT` — canonical BI mapping.
- `A1_ORCHESTRATOR` — orchestration wrapper that, when running, is
  authoritative over `BI_MAPPER_DEFAULT`.

Call `cdp_get_last_run_status` (or equivalent status tool) for each, compare
`request.eventDate`, and return the newer one. If `A1_ORCHESTRATOR` is in
`RUNNING` state, prefer it regardless of `BI_MAPPER_DEFAULT`'s timestamp.

### 4.7 Excel pivot export

Cube reports expose a special export endpoint that returns a binary file:

```
POST reportDefs?action=exportExcelPivot&cubeId=<cube>
body: {"password": "<pw>", "filename": "<name>"}
Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

The MCP does not expose binary download as a tool today; if needed, use the
generic `cdp_raw_request` (if available) or add a dedicated tool. `cubeId` is
mandatory and must match the cube whose pivot is being exported.

---

## 5. SQL-query (sQueryDef) reports

SQL reports are report defs whose `sQueryDef` field describes a parameterized
SQL query. Before saving/sending, the UI validates that every `required`
argument has a value:

```
for arg in sQueryDef.arguments:
    if arg.required and arg.operator not in ("OP_NULL", "OP_NOT_NULL"):
        assert arg.values[0] is not None
        if arg.operator in ("OP_BETWEEN", "OP_IN_RANGE_OF"):
            assert arg.values[1] is not None
```

If an argument is optional and empty, send `values: []` (not `null`, not
`[null]`). The MCP will not validate this for you; the backend will reject
missing required inputs with a 400.

### UDMP resource lookup for entity binding

SQL reports bind to UDMP tables by `tableId`. Vega caches the full resource
list on first use and looks up by `tableId`:

```
GET configAPI UDMPResources → list
resource = find r where r.tableId == report.sQueryDef.tableId
sQueryDef.resourceName = resource.name
```

Resolve the `name` before posting the sQueryDef.

---

## 6. Multi-report merge (dashboard widgets spanning reports)

`getMultiReportData` (dashboard) issues **parallel** fetches for all widgets
and then concatenates `dataset` arrays. Before concat it validates the schema
is compatible:

```
base_attrs = {a.name for a in reports[0].attributes}
for r in reports[1:]:
    assert all(a.name in base_attrs for a in r.attributes)
```

If a dashboard mixes incompatible reports the UI surfaces a single error
("Reports have incompatible schemas"). For MCP consumers: if you plan to
aggregate widget datasets, compare `attributes` first — the server will
happily return mismatched schemas.

---

## 7. Minimum tool set for a full dashboard workflow

| Step | MCP tool |
|------|----------|
| List folders | `cdp_list_folders` (`campaign/folders?type=DashboardDef`) |
| Save a report def | `cdp_create_report_def` / `cdp_update_report_def` |
| Create a dashboard | `cdp_create_dashboard` |
| Load dashboard graph | `cdp_get_dashboard` + `cdp_get_report_def` (per widget) |
| Execute an ad-hoc cube query | `cdp_execute_report` |
| Fetch cached cube/SQL result | `cdp_fetch_report_data` |
| Check cube freshness | `cdp_get_cube_status` |
| Send-now a report | `cdp_run_workflow("REPORT_RUNNNER_DEFAULT", ...)` |
| Schedule a report | `cdp_create_schedule` + `cdp_invoke_workflow_action("REPORT_RUNNNER_DEFAULT", action="schedule", ...)` (see orchestration playbook §1.3) |

---

## 8. Failure modes you will hit

- **400 `content is missing`**: forgot to wrap the body in `[...]` on POST.
- **400 `invalid model`** from cube execute: `cubicSetDef.model` was sent as an
  object instead of a stringified JSON.
- **404 `REPORT_RUNNER_DEFAULT not found`**: you spelled the workflow with two
  Ns instead of three. Correct: `REPORT_RUNNNER_DEFAULT`.
- **Report saved but orphaned in UI**: forgot `?folderId=` on save.
- **Dashboard loads but cells are blank**: didn't parse `uiProperties` back
  into `layout`.
- **Stale cube data**: `cubeStatus` shows fresh but `?action=fetch` returns
  old rows → `A1_ORCHESTRATOR` is still running. Check both workflows.

