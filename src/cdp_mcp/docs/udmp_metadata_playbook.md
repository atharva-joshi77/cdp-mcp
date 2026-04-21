# UDMP, Metadata & Tenant Properties Playbook

Authoritative flow for managing UDMP tables & columns, column validators,
mapping templates, content-model templates, and tenant properties — derived
from:

- `ui-core/src/app/services/udmp/udmp.service.js`
- `ui-config/src/app/main/udmp/udmp.controller.js`
- `ui-config/src/app/main/udmp/column-validators-data.service.js`
- `ui-config/src/app/main/mapping-templates/mapping-templates-data.service.js`
- `ui-config/src/app/main/content-models/content-models.service.js`
- `ui-config/src/app/main/tenantProperties/tenant-properties.controller.js`

Covers non-obvious sequencing, batch-write pitfalls, schema-publish ordering,
and tenant-property access gates.

---

## 1. UDMP tables: the nested-columns shape

A UDMP table read (`GET UDMPTables?include=columns`) returns:

```
{
  tableId: 17,
  name: "customer",
  columns: {
    content: [ {columnId, name, dataType, ...}, ... ]   // paged response
  },
  ...
}
```

**Before saving**, the UI flattens `columns.content` into `columns`:

```js
if (table.columns && angular.isArray(table.columns.content)) {
  table.columns = table.columns.content;
}
```

And then restores the nested shape on failure:

```js
on error: table.columns.content = table.columns;
```

MCP callers must do the same flatten-before-write, nest-after-read. POST/PUT
with the `{content: [...]}` wrapper returns 400 "columns malformed".

---

## 2. Batch save (`saveResources`) = parallel POST/PUT/DELETE

`UDMPDataService.saveResources(resourceName, keyField, createArr, updateArr,
deleteArr)` issues one request per item, **in parallel** via `vegaHttp.all`:

```
for t in createArr:  POST {resource}            body: t
for t in updateArr:  PUT  {resource}/{t[key]}   body: t
for t in deleteArr:  DELETE {resource}/{t[key]}
```

This pattern is used for:

| Resource | `keyField` |
|----------|-----------|
| `UDMPTables` | `tableId` |
| `UDMPResources` | `resourceId` |
| `columnValidators` | `id` |

### Consequences for MCP consumers

- There is **no** bulk endpoint. To replicate a 50-change batch you issue 50
  parallel requests.
- Failures are **not** transactional. If 3 of 10 requests fail, the other 7
  succeed and the UI surfaces per-item errors. Callers must track which
  requests failed and decide whether to retry, roll back (by issuing
  opposite operations), or accept partial state.
- Ordering inside the batch is unspecified. Don't rely on create-before-update
  ordering for cases where the updated row depends on a newly created one —
  split into two serial batches.

### Derived cascade: `UDMPTables` → `UDMPResources`

The UDMP controller has a second-pass handler `updateUMDPResources(responses)`
that inspects each response from the primary `UDMPTables` batch and issues a
*second* `saveResources('UDMPResources', ...)` batch to keep resource rows in
sync:

- New table with `udmpResource` set → create a matching resource row.
- Renamed `udmpResource` → update the resource row.
- Table deleted → delete the resource row.

The MCP does not orchestrate this cascade. If you modify UDMP tables via the
MCP, you must also call `cdp_create_udmp_resource` / `cdp_update_udmp_resource`
/ `cdp_delete_udmp_resource` yourself. Skipping this leaves orphan resource
rows that make sQueryDefs unable to resolve table names.

---

## 3. Schema publish ordering

UDMP edits are a **two-phase** model: changes land in the "unpublished"
zone until a schema publish sweeps them into production.

```
1. saveResources('UDMPTables', 'tableId', creates, updates, deletes)
2. cascade: saveResources('UDMPResources', ...) if needed
3. POST schemaCheckpoints?action=publish  (or equivalent publish workflow)
```

The UI's `getLatestSchemaRevision()` returns `schemaColumnIncrement` — any
`columnId > schemaColumnIncrement` is flagged `unPublished`. After publish,
the increment advances and those columns become canonical.

Before publishing:

- **All downstream cube/SQL reports must be paused** or they will run against
  an inconsistent schema during the swap.
- **All input connectors** targeting new columns should be **unpublished**
  (see connector playbook §3 `unpublish`) until the schema is stable —
  otherwise in-flight loads can fail validation.

There is no atomic "publish everything with rollback" — treat publish as a
forward-only step and validate via dry-run first (see admin-ops playbook's
compaction dry-run pattern).

---

## 4. Custom-attribute entity gate

Custom columns (prefix `c_`) can be added only to tables in the tenant-level
whitelist:

```
GET tenantProperties
filter: {propertyGroup: 'UDM+', propertyName: 'summaryEntity.customAttribute.whitelist'}
→ propertyValue = "customer,subscription,transaction"
```

The UI blocks "New Column" for tables whose `name` is NOT in the whitelist
AND whose name matches `/summary\b/`. MCP callers composing tables should:

1. Fetch the whitelist first via `cdp_get_tenant_property("UDM+",
   "summaryEntity.customAttribute.whitelist")`.
2. If target table name is not in the whitelist and its name ends in
   `summary`, **do not** call `cdp_add_udmp_column` — it will be rejected or
   (worse) silently shadowed by a read-only definition.

Bulk column add accepts a JSON-array-as-name syntax:

```js
if (name starts with "[" and ends with "]") {
  names = JSON.parse(name)   // ["c_foo","c_bar"]
  // one row per name, displayName derived from name
}
```

The MCP does not expose this shortcut — call `cdp_add_udmp_column` once per
name.

---

## 5. Column validators: batch save + idempotent PUT

`ColumnValidatorsDataService.saveResources(creates, updates, deletes)` uses
the same parallel POST/PUT/DELETE pattern as UDMP tables. The oddity:

- `createColumnValidator(data)` → `POST columnValidators`
- `updateColumnValidator(id, data)` → `PUT columnValidators/{id}`
- `updateTableProperties(table)` (table-level overrides) →
  `PUT UDMPTables/{tid}/tableoverrides` regardless of whether the override
  row exists — the backend upserts.

The `tableoverrides` idempotent PUT is unusual and worth remembering: there
is **no** "create override" endpoint. Always use PUT.

---

## 6. Mapping templates (connector field mapping presets)

Simple CRUD against `mappingTemplates`:

| Method | Path |
|--------|------|
| GET | `mappingTemplates?offset=0&limit=500` |
| POST | `mappingTemplates` (body = template) |
| PUT | `mappingTemplates/{templateId}` |
| DELETE | `mappingTemplates/{templateId}` |

No batch endpoint. Mapping templates referenced by a connector cannot be
deleted — the backend throws FK-violation 409. The UI defends against this
with a confirm dialog that lists dependent connectors; MCP callers should do
the equivalent precheck via `cdp_list_connectors` filtered by the template
id.

---

## 7. Content models (`campaignAPI templates`)

Content models live under `campaignAPI`, not `reportAPI`. Two list endpoints:

| Path | Semantic |
|------|----------|
| `templates/fetchAll?type=<t>` | All templates of a type (usually used for admin) |
| `templates?type=<t>&fields=["properties"]` | Lean projection — just the fields you need |

The `fields` parameter is a URL-encoded JSON array: `%5B%22properties%22%5D`.

### Bulk update: PUT with action query

The write path is the odd one:

```
PUT templates/provision?action=update
body: <updatePayload>   # structure depends on template type
```

- **PUT**, not POST — even though the URL carries `?action=update`.
- Body is NOT wrapped in an array (unlike reports/dashboards).
- Returns updated rows in `response.data`.

Do not try `POST templates?action=update` — it either 404s or silently
dispatches to a different provisioning flow.

---

## 8. Tenant properties

```
GET configAPI tenantProperties                          → all properties (grouped client-side by propertyGroup)
GET configAPI tenantProperties/{propertyId}
POST configAPI tenantProperties                         body: property    (create; auto-assigns propertyId)
PUT  configAPI tenantProperties/{propertyId}            body: property    (update)
DELETE configAPI tenantProperties/{propertyId}
```

### JSON property values

When a property value is itself a JSON document, the UI enforces
client-side parse validation (`vm.onValidateJson`). The stored value is
still a **string** — don't `json.loads` the `propertyValue` unless you know
the property type is JSON.

### Protected property: `customer360 / default.360.layout`

This property is read-only for non-default tenants:

```js
if (tenantId != 0 && propertyGroup == 'customer360' && propertyName == 'default.360.layout') {
    block save;
}
```

The tenant-level override is `customer360 / tenant.360.layout` (see the
customer-360 playbook for the merge semantics).

MCP rule:

- **Never POST** `customer360 / default.360.layout` for a real tenant. It is
  only settable at the platform/default tenant level.
- **Always use** `customer360 / tenant.360.layout` to customize a real tenant's
  layout.
- Internal properties (`internal == true`) are rendered read-only in the UI
  and PUT against them fails with 403.

### Grouping convention

Tenant properties are grouped by `propertyGroup`. Known groups:

| Group | Purpose |
|-------|---------|
| `customer360` | 360 layout, default / tenant overrides |
| `UDM+` | UDMP feature flags (`summaryEntity.customAttribute.whitelist`) |
| `campaign` | Campaign defaults |
| `connector` | Connector defaults |
| `reports` | Report defaults |
| `security` | Token lifetimes, SSO flags |

Queries like "get the 360 layout for this tenant" = merge of two reads:

```
GET tenantProperties then filter group=customer360, name=default.360.layout
GET tenantProperties then filter group=customer360, name=tenant.360.layout
```

Deep-merge them in that order (default first, tenant overrides second) with
the rules documented in the customer-360 playbook.

---

## 9. Minimum tool set

| Task | Tool |
|------|------|
| List UDMP tables | `cdp_list_udmp_tables` |
| Create/update/delete table | `cdp_create_udmp_table` / `cdp_update_udmp_table` / `cdp_delete_udmp_table` |
| List UDMP resources | `cdp_list_udmp_resources` |
| List/manage column validators | `cdp_list_column_validators` / `cdp_create_column_validator` / `cdp_update_column_validator` / `cdp_delete_column_validator` |
| Table-level overrides | `cdp_update_udmp_table_override` (PUT upsert) |
| Mapping templates | `cdp_list_mapping_templates` / CRUD |
| Content-model templates | `cdp_list_templates` / `cdp_provision_templates` (PUT `?action=update`) |
| Tenant properties | `cdp_list_tenant_properties` / `cdp_create_tenant_property` / `cdp_update_tenant_property` / `cdp_delete_tenant_property` |
| Schema checkpoints | `cdp_get_schema_checkpoints` / `cdp_publish_schema` |

---

## 10. Failure modes you will hit

- **400 "columns malformed"**: sent `columns: {content: [...]}` instead of
  `columns: [...]` on PUT UDMPTables.
- **Custom column silently not created**: target table isn't on the
  `summaryEntity.customAttribute.whitelist`.
- **Orphan UDMP resource rows**: modified UDMP tables via the MCP without
  triggering the cascade described in §2.
- **`templates/provision?action=update` returns 405 method-not-allowed**: you
  used POST; it must be PUT.
- **Default 360 layout won't save**: you targeted a real tenant. Default layout
  is platform-level only; use `tenant.360.layout` for tenant overrides.
- **Partial failure in batch save**: `saveResources` is not transactional.
  Expect M-of-N failures and code for them.

