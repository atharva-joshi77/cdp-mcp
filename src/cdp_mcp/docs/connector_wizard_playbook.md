# Connector Wizard Playbook

Authoritative flow for creating, updating, publishing, scheduling, and
unscheduling CDP connectors (input and output) — derived from:

- `ui-core/src/app/services/connector/connector.service.js`
- `ui-config/src/app/main/connector/input-connectors/input-connector-controller.js`
- `ui-config/src/app/main/connector/output-connectors/*`
- `ui-config/src/app/main/connector/wizard/connector-wizard.tmpl.html`

Covers every subtle rule an LLM chaining `cdp_create_connector`,
`cdp_publish_connector`, `cdp_create_schedule`, and `cdp_invoke_workflow_action`
will otherwise get wrong.

---

## 1. Input vs output connector endpoint swap

All CRUD routes come in parallel pairs. Picking the wrong half silently writes
into the wrong table — you won't get an error, just the wrong result.

| Concept | Input path | Output path |
|---------|-----------|-------------|
| CRUD | `connectors` | `outputConnectors` |
| Definitions (read-only catalog) | `connectorDefs` | `outputConnectorDefs` |

The MCP exposes `cdp_list_connectors` / `cdp_list_output_connectors` (etc.)
as distinct tools — use the correct one for the direction you're working in.
If you only have a generic `cdp_list_connectors` and an `is_output` flag,
verify the flag maps to the `outputConnectors` endpoint.

---

## 2. The wizard is 4 or 5 steps depending on connector type

The Vega-Config wizard tracks `selectedStep`, `stepProgress`, and `maxStep`.
The step set is fixed up-front but extended conditionally in edit mode:

```
default steps = [Definition, Parameters, Mapping, "Record Count Alerts"]
if selectedConnectorDef.ssidPrefix in intervalConnectors and editMode:
    steps.push("Interval Configuration")
```

Constants (copy verbatim from `input-connector-controller.js`):

```js
inputConnectorsToSkip = ['API_DWAPI', 'API_P360'];
intervalConnectors = [
  "ESP_ETG", "ESP_CHT", "WEB_AS3", "ESP_RSP", "ESP_BRT", "ESP_SEL",
  "ESP_SPOP", "ESP_EUM", "GAC_API", "ESP_LST", "GA4_API"
];
```

Implications for MCP consumers:

- Do **not** offer to create connectors whose `ssidPrefix` is in
  `inputConnectorsToSkip` — those are virtual/internal and the wizard filters
  them out on purpose.
- When updating an `intervalConnectors` connector (webtag or ESP), you must
  also set `epochMinInterval`, `epochMaxInterval`, and `epochBacktrack` — the
  Interval Configuration step is not optional for these; omitting them causes
  the runner to fetch 0 rows forever.
- `GAC_API` is not in `intervalConnectors` but still requires `showAllTables =
  true` handling — its parameter schema exposes all UDMP tables rather than
  the default subset.

---

## 3. The create → (optional) publish pattern

Creating a connector does not make it usable — data won't flow until the
connector is *published*. The UI performs these as **two separate HTTP
calls**:

```
1. POST connectors                  body: <connector>
2. (if publish checkbox): POST workflows/CONNECTOR_OPS_DEFAULT
                            ?entityType=connector&entityId=<newId>&action=publish
```

Response from step 1 gives you `response.data.connectorId`, which is what
step 2 uses as `entityId`.

**The MCP equivalent**:

```
new_id = cdp_create_connector(body=...).connectorId
cdp_invoke_workflow_action(
    workflow_name="CONNECTOR_OPS_DEFAULT",
    action="publish",
    params={"entityType": "connector", "entityId": new_id},
)
```

### `unpublish`

Mirror action: `action=unpublish`. Required before deleting a connector that
has ever been published — otherwise a phantom "active publication" row is
left behind.

---

## 4. Schedule creation is a **3-step** orchestration

This is the single most error-prone flow for MCP callers. `cdp_create_schedule`
alone does **not** make a connector run on schedule. Three actions must occur
in order:

### Step 1. Resolve the AIF_RUNNER entity id (one-time per session)

```
GET workflows/AIF_RUNNER → response.data.id   # numeric DB id, cache it
```

This is `service.aifWorkflowEntityId` in the Vega source. Treat it as a
session-level cache.

### Step 2. Create the schedule row

```
POST schedules
body: {
  referenceId:  <aifWorkflowEntityId>,   # NOT the connector id
  type:         "WORKFLOW",
  startTime:    "00:00",
  active:       true,
  scheduleName: "Schedule-<ms>",         # UTC millis suffix is the UI convention
  entityId:     <connectorId>,
  entityType:   "connector",
  ...user fields (period, frequency, startDateObj, startTimeObj)
}
→ response.data.scheduleId
```

Field-by-field gotchas:

- `referenceId` = the **runner workflow's numeric DB id**, not the connector.
  Confusing `referenceId` with `entityId` is the #1 MCP mistake here.
- `type` = `"WORKFLOW"` verbatim.
- `startTime` = `"00:00"` as a sentinel; actual schedule cadence comes from
  `period`/`frequency`/`startDateObj`/`startTimeObj`.
- `scheduleName` = `"Schedule-" + new Date().getUTCMilliseconds()`. The UI
  uses this to generate a unique (albeit collision-prone) name. A human-readable
  alternative is fine; the backend only requires uniqueness.

### Step 3. Arm the runner workflow

```
POST workflows/AIF_RUNNER
  ?entityType=connector
  &entityId=<connectorId>
  &action=schedule
  &scheduleId=<newScheduleId>
```

**Only after step 3** does the scheduler actually pick up the connector. A
schedule row created without step 3 is inert — it appears in `GET schedules`
but no job ever runs.

### MCP mapping

```
runner_id = cdp_get_workflow("AIF_RUNNER").data.id
sched    = cdp_create_schedule(body={
    "referenceId": runner_id,
    "type": "WORKFLOW",
    "startTime": "00:00",
    "active": True,
    "scheduleName": f"Schedule-{int(time.time_ns() // 1_000_000) % 1000}",
    "entityId": connector_id,
    "entityType": "connector",
    "period": "DAY",   # user input
    "frequency": 1,
    "startDateObj": "...",
    "startTimeObj": "...",
}).scheduleId
cdp_invoke_workflow_action(
    workflow_name="AIF_RUNNER",
    action="schedule",
    params={"entityType": "connector",
            "entityId": connector_id,
            "scheduleId": sched},
)
```

---

## 5. Schedule deletion is a **reverse 2-step** orchestration

The UI performs:

```
1. POST workflows/AIF_RUNNER
     ?entityType=connector&entityId=<cid>
     &action=unschedule&scheduleId=<sid>

2. DELETE schedules/{sid}
```

If you invert the order, step 1 fails with "schedule not found" because the
runner workflow looks up the schedule row; and you've already deleted it.
The connector is now orphaned with a dangling `entityType=connector` binding
on the runner.

### MCP mapping

```
cdp_invoke_workflow_action(
    workflow_name="AIF_RUNNER",
    action="unschedule",
    params={"entityType": "connector", "entityId": cid, "scheduleId": sid},
)
cdp_delete_schedule(schedule_id=sid)
```

---

## 6. Schedule update (no runner touch required)

Changing `active`, `period`, `frequency`, etc. on an existing schedule is a
plain `PUT schedules/{id}`. No runner-workflow action is needed because the
binding was established at creation. Exception: if you flip `active` from
`false` → `true` on a schedule that was previously **unscheduled** (step 1 of
§5 was called), you must re-arm via `action=schedule` again.

The safer path is to always pair `active=false` with a full `unschedule` and
`active=true` with a full `schedule` invocation.

---

## 7. History and summary

```
GET connectors/{id}/summary                → latest run + health
GET connectors/{id}/history?offset=0&limit=50  → paginated run history
```

`history` is **not** part of the generic job list — it's a connector-specific
endpoint. Use `cdp_get_connector_history` rather than the generic orchestration
status endpoint when you want counts of records processed per run.

---

## 8. Mapping payload shape

Connector `mapping` is an array of `[entityInfo, [mappedColumns]]` pairs
(note: it is a 2-tuple-of-arrays, not an object):

```
mapping: [
  [ {table: "customer", type: "group"}, [
      {sourceColumn: "cust_id", targetColumn: "sourcecustomernumber", dataType: "string"},
      ...
    ]
  ],
  [ {table: "transaction", type: "group"}, [ ... ] ]
]
```

`buildMappingEntities()` (in `connector.service.js`) is the transformer that
the UI runs on read; it decorates each column with `type: 'column'` and flags
the group as `collapsed: true` for rendering. **Do not** save those UI
decorations back to the server — strip them before POST/PUT.

`getMappedColumns(entityColumns)` is the symmetric write-side transformer;
its output is the `mapping` array above.

---

## 9. Parameter completion rule

When you PUT an updated connector, every parameter listed in the connector
*definition* must be present, even if the user didn't change it. The UI's
`addMissingParams(connectorParams, connectorDef)` merges any
`parameterDefs[]` entries that are missing from the saved connector, falling
back to `parameter.defaultValue`:

```python
for pd in connector_def.parameters:
    if not any(p.name == pd.name for p in connector.parameters):
        connector.parameters.append({**pd, "value": pd.defaultValue})
```

Before sending, ensure every parameter has a non-null `value`:

```python
for p in connector.parameters:
    if p.value is None:
        p.value = ""
```

Empty-string is required — `null` or omitted key fails validation.

---

## 10. Data-start timestamp

For new connectors (not edits), the UI sets `dateStarted = Date.now()` before
the first POST. This tells the runner how far back to scan. If you omit it,
the runner defaults to *epoch 0*, causing the first run to attempt to ingest
the entire source.

```python
if not edit_mode:
    connector["dateStarted"] = int(time.time() * 1000)
```

---

## 11. Validate & Save sequence summary

```
1. GET connectorDefs                      # cache once
2. GET UDMPTables                         # for mapping targets
3. (edit) GET connectors/{id}             # load existing
4. validate name uniqueness, parameters, mapping
5. if new:  POST connectors               body: <assembled connector>
   if edit: PUT  connectors/{id}          body: <assembled connector>
6. if publish checkbox:
       POST workflows/CONNECTOR_OPS_DEFAULT?...action=publish
7. if schedule dirty:
       (§4) create / (§5) delete / (§6) update schedule
```

Skipping step 1 means you'll pick wrong `connectorDef.id`; skipping step 2
means the UI can't compose a valid `mapping`.

---

## 12. Failure modes you will hit

- **Connector created but no data flows**: forgot step 6 (publish).
- **Schedule row exists but no job runs**: forgot step 3 of §4 (arm
  AIF_RUNNER).
- **Delete schedule returns 400 "schedule not found"**: deleted the row
  before unscheduling. Run `action=unschedule` first on whatever connector/entity
  still references it — or accept the orphan row.
- **Runner scans entire history on first run**: omitted `dateStarted`.
- **500 on update**: sent connector with `mapping` still carrying UI keys
  (`type`, `collapsed`, `$$hashKey`). Strip them.
- **"Invalid Increment Value"**: `epochMinInterval` collision with another
  connector. Each interval connector must have a unique increment. The UI
  validates this client-side with `validateIncrementValue(connector)`.

