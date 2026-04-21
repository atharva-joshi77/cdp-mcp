# CDP Customer 360 Playbook

Recipes for retrieving, rendering, and mutating customer identity data via the MCP. Reverse-engineered from `ui-vega/src/app/main/customer360/services/customer360.service.ts` (~900 lines of orchestration) and `ui-config/src/app/main/360/customer360-data.service.js`.

Exposed as MCP resource `cdp://docs/customer360-playbook`.

## 1. The three parallel fetches

A profile page is NEVER the result of a single call. `getCustomerProfileData()` dispatches three promises in parallel and only renders when all three resolve:

| # | Call                                                              | MCP tool                                                   | Purpose |
|---|-------------------------------------------------------------------|------------------------------------------------------------|---------|
| 1 | GET `dw/a360/customers/{cid}?limit=&offset=&targetentity=`        | `cdp_get_customer_360_detail`                              | Raw customer data keyed by JSON resource descriptors. |
| 2 | GET `config/UDMPTables` (filtered to 14 specific tables)          | `cdp_list_udmp_tables` + filter                            | Column metadata for rendering. |
| 3 | GET `config/tenantProperties` keys `customer360/default.360.layout` and `customer360/tenant.360.layout` | `cdp_get_tenant_property` (one per key) | Layout template, deep-merged. |

**Why this matters for an MCP agent:** if you only call #1 you receive a dict keyed by stringified JSON objects like `'{"displayResourceKey":"$customer","resource":"customer","layout":"customer"}'`. Without the UDMP metadata and layout you cannot interpret it.

### 1.1 Required UDMP tables

Always request these 14 as a batch (hard-coded in `customer360.service.ts:441`):

```
household, householdsummary, address, customeraddressxref, customer,
subscription, customersummary, product, transactionitem, transaction,
event, message, organization, mastercustomergroupsummary
```

### 1.2 Layout merge rule

`default.360.layout` is the vendor default; `tenant.360.layout` is a sparse patch. Merge rules (from `mergeDeep`):

- Objects: recursive merge.
- Arrays of items with a `udmColumn` key: match by `udmColumn` (case-insensitive) and `Object.assign`.
- Arrays of items with `overwriteAtIndex`: replace `srcValue[overwriteAtIndex]`.
- Arrays of items with `mergeAtIndex`: recursive merge at `srcValue[mergeAtIndex]`.
- Anything else: `push`.

If you skip this merge, tenant customisations (renamed fields, hidden sections) are lost and the payload contains columns a user doesn't have permission to see.

## 2. Canonical retrieval sequence

```text
# Step 1: fetch in parallel
profile  = cdp_get_customer_360_detail(customer_id=cid, limit=50)
udmp     = cdp_list_udmp_tables()   # filter to the 14 above
defLay   = cdp_get_tenant_property(namespace="customer360",
                                   key="default.360.layout")
custLay  = cdp_get_tenant_property(namespace="customer360",
                                   key="tenant.360.layout")

# Step 2: merge layouts (implement mergeDeep locally)
layout = merge_deep(json.loads(defLay), json.loads(custLay))

# Step 3: transform profile keys
# Raw keys look like: '{"displayResourceKey":"$customer","resource":"customer","layout":"customer"}'
# Parse each key as JSON and use `.resource` to route to a layout section.
for key, values in profile.items():
    if key in {"customerIds", "householdCustomerIds", "realtimeData",
              "masterCustomerGroupMasterCustomerIds"}:
        continue   # passthrough
    meta = json.loads(key)
    section = layout[meta["resource"]]
    # attach values[...].values to section by matching udmColumn
```

## 3. Realtime layer

Separate endpoint: `GET dw/a360/customers/{cid}/rt` (use `cdp_get_customer_360_realtime`). Add `If-Modified-Since: <epoch-ms>` for incremental polling. The UI polls every ~5s while the profile page is open.

Realtime payload is shaped like:
```json
{
  "event":     [ {...event properties...} ],
  "customer":  [ {...overlay attrs...} ],
  ...
}
```
It's ADDITIONAL to the warehouse customer — merge by unioning the `event` list and letting `realtimeData.customer[0]` override `parsedData.customersummary` only if the warehouse row is empty.

## 4. Paging large resources

When `limit` > ~200 the server caps at 200. To walk all events for a customer:

```text
offset = 0
limit  = 200
while True:
    batch = cdp_get_customer_360_detail(
        customer_id=cid, limit=limit, offset=offset,
        target="event")   # ← narrows the query to one resource
    if not batch.get(event_key): break
    offset += limit
```
`targetentity` is the UI's scoping param — without it every page returns the full household+transaction+event payload and pagination is pointless.

## 5. Customer search

### 5.1 Basic
```text
GET dw/a360/customers?searchTerm=<str>*&limit=10&offset=0
```
`*` wildcard is appended by the UI on the basic search. MCP equivalent: `cdp_search_customer_360(search_term="smit", limit=10)`.

### 5.2 Advanced multi-field
The UI serialises into a single `fq` param:
```
fq=[{"lastname":["eq","jones*"],"firstname":["eq","caitlin*"],"email":["eq","caitlin.jones*"]}]
```
Rules (from `customerAdvSearch`):
- `sourcecustomernumber`, `email`, `address1`, `address2` → `encodeURIComponent`.
- `sourcecustomernumber`, `address*`, `primaryphone` → exact match (no trailing `*`).
- Other fields get `"<value>*"` wildcard.
- If `exactMatch=true` is toggled, ALL fields drop the `*`.

Pass the `fq` as a single pre-built string on the MCP call.

## 6. Customer identity purge (GDPR)

```text
cdp_request_data_erasure(body=json.dumps({
  "customerIds": ["KFK_0_user@example.com"],
  "reason": "GDPR right to erasure",
  "requester": "agent@tenant.example"
}))
```
The UI sets `httpConfig.skipErrorMessage = true` — the request is async and a 202/404 race is normal in the first ~10 seconds. Poll with `cdp_get_data_erasure_status_by_id`.

## 7. A360 rule administration (admin side)

Source: `A360RuleDataService.saveResources`.

The admin UI batches `(creates, updates, deletes)` into a single `vegaHttp.all`. MCP has no batch endpoint — implement client-side in the correct order:

```text
1. creates     cdp_create_a360_rule(...)   # add new customisation rules
2. updates     cdp_update_a360_rule(...)   # modify existing
3. columns     cdp_update_a360_rule_column(...)  # PUT a360Rules/columns/{id}
4. deletes     cdp_delete_a360_rule(...)
```
Reverse order (delete first) breaks FK checks when another rule references the column being removed.

## 8. Layout validation (admin side)

`validate360()` checks every `udmColumn` in the merged layout against the set of columns declared by active `a360Rules`. Agents should replicate this before pushing a new layout:

```text
rules  = cdp_list_a360_rules()
known  = { f"{col.tableName}.{col.columnName}".lower()
           for r in rules for col in r.customizationColumns }
for udm_col in walk_layout(layout):
    if udm_col.lower() not in known:
        flag(udm_col)    # will not render at runtime
```

## 9. Snowflake-enabled tenants

`TenantProperties.customer360.snowflake.a360.enabled == 'true'` changes date formatting only (timestamps arrive as UTC `moment` values, not epoch-ms). MCP-side this is cosmetic — keep dates as ISO strings and let downstream tooling format.

## 10. Minimum tool set for "render a customer"

- `cdp_get_customer_360_detail` (primary profile)
- `cdp_get_customer_360_realtime` (RT overlay)
- `cdp_list_udmp_tables` (column metadata)
- `cdp_list_a360_rules` (to know which columns are valid)
- `cdp_list_tenant_properties` or a specific `get_tenant_property` (for the two layout blobs)

Without ALL of these you cannot render a faithful profile — the raw `dw/a360` response alone is essentially uninterpretable JSON.

