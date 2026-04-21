# CDP Campaign Playbook (authoritative)

This document is the source of truth for creating campaigns, audiences, and messages on Acquia CDP via this MCP server. It's exposed to any MCP client as resource `cdp://docs/campaign-playbook`.

## Golden rule

**A campaign OWNS its audience and messages. They are inline, not shared.**

Do **not** use `cdp_create_audience_def` (endpoint is not supported: `POST /campaign/audienceDefs` → `E400 Request method 'POST' is not supported`).

Do **not** create a standalone `messageDef` and reference it by `resourceId` from a campaign. The server rejects shared references:
`E0420 FOUND_BAD_DATA_ERROR: MessageDef already exists outside of the Campaign. MessageDefs may only exist in a parent CampaignDef, and may not be shared.`

## Canonical workflow

1. `cdp_create_campaign(name, description)` — bare shell. Returns a new `resourceId`.
2. `cdp_update_campaign(campaign_id, body=<JSON string>)` — PUT the full campaign with **inline** `audience` and **inline** `messageDefs` objects. The server assigns resourceIds to children.
3. `cdp_get_campaign(campaign_id)` to verify.
4. (Optional) `cdp_execute_audience_def` / `cdp_calculate_audience` to size the audience.
5. `cdp_start_campaign(campaign_id)` when ready to launch.

## Canonical campaign body

```json
{
  "name": "...",
  "description": "...",
  "tenantId": 802,
  "campaignType": "CAMPAIGN",
  "iconURL": "GoWild.png",
  "audience": {
    "operandType": "DatasetDefOperation",
    "tenantId": 0,
    "operator": "INTERSECTION",
    "arguments": [
      {
        "operandType": "DatasetDef",
        "type": "CUSTOMER",
        "category": "AudienceDef",
        "opaque": false,
        "tenantId": 0,
        "input": {
          "inputType": "ENTITY",
          "entityName": "customersummary",
          "filter": { /* see filter patterns below */ },
          "interactionType": ["CRITERIA"],
          "outputAttributes": [
            {"name": "MasterCustomerID", "entity": "customersummary",
             "metadata": {}, "static": false, "rank": false, "displayable": false}
          ],
          "operation": {"operator": "DISTINCT"},
          "metadata": {}
        }
      }
    ]
  },
  "audienceContent": [
    {"name": "email",     "entity": "customersummary", "metadata": {}, "static": false, "rank": false, "displayable": false},
    {"name": "FirstName", "entity": "customersummary", "metadata": {}, "static": false, "rank": false, "displayable": false},
    {"name": "LastName",  "entity": "customersummary", "metadata": {}, "static": false, "rank": false, "displayable": false}
  ],
  "messageDefs": [
    {
      "tenantId": 802,
      "channel": "A1M",
      "subject": "...",
      "fromAddress": "hello@brand.com",
      "fromName": "Brand Team",
      "message": "<html>...</html>"
    }
  ],
  "connectorId": 12,
  "connectorListId": 0,
  "properties": [],
  "content": [],
  "variants": [],
  "segmentationCriteriaDefs": [],
  "segmentDefs": []
}
```

## DatasetDef operator enum (valid values)

Comparison operators use the `_EQUALS` suffix, **not** `_OR_EQUAL`:

- Equality / ordering: `EQUALS`, `NOT_EQUALS`, `LESS_THAN`, `LESS_THAN_EQUALS`, `GREATER_THAN`, `GREATER_THAN_EQUALS`
- Boolean: `AND`, `OR`, `NOT`
- Set / range: `IN`, `NOT_IN`, `BETWEEN`, `LIKE`, `MATCHES`, `NOT_MATCHES`, `CONTAINS`, `NOT_CONTAINS`, `BEGINS_WITH`, `ENDS_WITH`, `EMPTY`, `NOT_EMPTY`, `IS_NULL`
- Arithmetic: `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `REMAINDER`
- Time: `NOW`, `FROM_UNIX_TIMESTAMP`, `IN_THE_LAST`, `IN_THE_NEXT`, `IN_THE_RANGE_OF`, `IN_THE_FUTURE_RANGE_OF`
- Aggregates / control flow: `SUM`, `COUNT`, `MODE`, `ARG_MIN`, `ARG_MAX`, `HAVING`, `GROUP_BY`, `DISTINCT`, `AT_LEAST`, `PASSED_ARGUMENT`

Using `LESS_THAN_OR_EQUAL` or `GREATER_THAN_OR_EQUAL` will fail with a JSON parse error.

## Time-window math

Use millisecond epoch arithmetic on timestamp attributes:

```
<attr> GREATER_THAN (NOW - <days> * 86400000)
```

Common constants:

| Window | ms |
|--------|----|
| 1 day  | `86400000` |
| 7 days | `604800000` |
| 14 days | `1209600000` |
| 30 days | `2592000000` |
| 60 days | `5184000000` |
| 90 days | `7776000000` |

Example — `TransactionTimeStamp` in the last 30 days:

```json
{"operator": "GREATER_THAN", "arguments": [
  {"attributes": ["TransactionTimeStamp"], "attributeTables": {}, "aggregateAttributes": [], "inputType": "ATTRIBUTES"},
  {"operation": {"operator": "SUBTRACT", "arguments": [
    {"operation": {"operator": "NOW", "arguments": []}, "inputType": "OPERATION"},
    {"value": "2592000000", "inputType": "VALUE"}
  ]}, "inputType": "OPERATION"}
]}
```

## "Has NOT done X in the last Y days" pattern

Use `customer` entity with `setOperation: EXCLUDE` between two `datasetDefInput` branches. First branch = target cohort, second branch = behavior to exclude.

Event string literals go in single quotes inside the `VALUE` node (e.g. `"value": "'emailOpened'"`).

Canonical winback (purchased in last 30 days, did not open email in last 14 days):

```json
"filter": {
  "datasetDefInput": {
    "inputType": "ENTITY",
    "entityName": "customer",
    "setOperation": {
      "operator": "EXCLUDE",
      "arguments": [
        { "datasetDefInput": { /* transaction in last 30 days */ }, "inputType": "DATASET_DEF_INPUT" },
        { "datasetDefInput": { /* event Type='emailOpened' in last 14 days */ }, "inputType": "DATASET_DEF_INPUT" }
      ]
    },
    "metadata": {}
  },
  "inputType": "DATASET_DEF_INPUT"
}
```

Reference campaign for this pattern: `resourceId 424` ("CampaignUpdate", cart-abandon).

## Discovering attributes without admin perms

`cdp_describe_entity` / `cdp_list_entities` often return `E401_ACCESS_DENIED`. Fallbacks:

1. Call `cdp_list_campaigns` for the tenant.
2. Walk the JSON for `{"inputType": "ATTRIBUTES", "attributes": [...]}` nodes.
3. Union of those arrays = attributes actually in use on this tenant.

Simple pre-computed attributes like `recency`, `DaysSinceLastOrder`, `daysSinceLastPurchase`, `DaysSinceLastEmailOpen` are **not** universally available. Do not assume — verify, or use event/transaction traversal.

## Body parameter convention

Every tool with a `body` parameter expects a **JSON string** (not a dict). The tool internally calls `json.loads(body)`. Passing a dict yields a pydantic validation error: `Input should be a valid string [type=string_type]`.

Tip: build the dict in code, then `json.dumps(obj)` once before handing it to the tool.

## Spam scoring

`cdp_score_spam` body must be a JSON **array**:

```json
[{"subject": "...", "body": "...", "fromAddress": "...", "fromName": "..."}]
```

Passing a single object returns `E400 Cannot deserialize from Object value`.

## Audience sizing

- `cdp_get_audience_count` (sync) works when the audience filters direct `customersummary` attributes. For event/transaction traversal shapes, it often returns `E500_DATASET_EXEC_FAILED`.
- Workaround: store the audience inline on a campaign, then `cdp_execute_audience_def` to compute via the workflow.
- `cdp_calculate_audience` (async, returns `jobId`) is the DW equivalent; poll with `cdp_get_calculated_count`.

## Reference campaigns to clone / pattern-match

| Pattern | Campaign resourceId |
|---------|---------------------|
| Simple `customersummary.age` template | `103663` ("DRF test 2") |
| `tenuredays` + `TotalTransactionCount` template | `422` ("bbb") |
| Event-traversal cart abandon (EXCLUDE pattern) | `424` ("CampaignUpdate") |
| Opaque `CustomerTemplate` | template `resourceId 1902` |

## UI-derived orchestration patterns (ui-vega + ui-config `2601-release`)

These sequences were extracted by inspecting the customer-facing Vega UI and
the admin Config UI. Every step mirrors what the UI does for the corresponding
user action — follow them to avoid contract mismatches.

### 1. Save campaign (always pass `folderId`)

Vega sends `?folderId=<id>` on **every** POST/PUT, even for root-folder saves
(`folderId=0`). Our tools accept an optional `folder_id`:

```
cdp_create_campaign(name=..., description=..., folder_id=0)
cdp_update_campaign(campaign_id=..., body=<json>, folder_id=0)
```

Omit it only if you have a good reason — some CDP builds reject saves with
no folder context.

### 2. Batch "Send now" vs. triggered/web "Publish"

Two completely different workflows — do **not** confuse them:

| Campaign kind | Tool | Backend call |
|---|---|---|
| Batch / cohort | `cdp_start_campaign` | `POST campaign/campaignDefs/run?entityId=<id>` body `{"campaignProperties":"{}"}` |
| Triggered / web | `cdp_publish_web_campaign` | `POST config/workflows/CAMPAIGN_FLOW_DEFAULT?action=run&entityType=campaign&entityId=<id>` body `{"campaignProperties":"{\"webAction\":\"PUBLISH\"}"}` |

Calling `cdp_start_campaign` on a web campaign silently no-ops on some builds.

### 3. Shared-datasetDef E400 recovery

If you clone/fork a campaign and the server returns:

> E400: The campaignDef being created refers to an existing datasetDef.
> Please correct this by calling `/v2/{tenantId}/datasetDef/{id}?action=copy`

…call `cdp_copy_datasetdef(dataset_def_id)` and embed the returned object
inline into the new campaign's `audience` field before `cdp_update_campaign`.

### 4. Data export save-then-run (mirrors Vega dataExport module)

```
cdp_create_data_export(body=<json>, folder_id=0)
cdp_update_data_export(export_id=..., body=<json>, folder_id=0)
cdp_run_data_export(export_id=...)
```

`cdp_run_data_export` auto-sends `{"dataExportProperties":"{}"}` — the
configapi `WorkflowController` requires a non-null `Map<String,String>`.

### 5. Async audience sizing (UI polling loop)

Vega uses async because sync `cdp_get_audience_count` fails on event-traversal
shapes:

```
jobId = cdp_calculate_audience(body=<audience json>)
# poll every 30s, back off to 120s after ~9 attempts:
cdp_get_calculated_count(job_id=jobId)
```

Treat a 202 / empty body as "still computing".

### 6. Generic workflow invocation

For ad-hoc workflows (PROVISIONER_TOOL_DEFAULT, custom tenant workflows):

```
cdp_run_workflow(
  workflow_id="PROVISIONER_TOOL_DEFAULT",
  entity_type="tenant",
  entity_id="802",
  body='{"provisionerProperties":"{}"}'
)
```

`body` was added specifically because several triggered workflows
(`*_FLOW_DEFAULT` variants) reject a null body.

### 7. Typical full lifecycle (from Vega campaign wizard)

1. `cdp_create_campaign(name, description, folder_id=0)` → returns `id`
2. `cdp_update_campaign(id, body=<full JSON inline audience+messageDefs>, folder_id=0)`
3. `cdp_calculate_audience(body=<audience subset>)` → poll `cdp_get_calculated_count`
4. Approval / review (out-of-band)
5. **Batch**: `cdp_start_campaign(entity_id=str(id), cohort=False)`
   **Web**: `cdp_publish_web_campaign(entity_id=str(id))`
6. Monitor via `cdp_get_run_dispatches(def_id=id)` + `cdp_list_campaign_runs(def_id=id)`
7. Kill if needed: `cdp_stop_campaign(campaign_id=id)`
