# CDP MCP — Audit Report

Target: `/Users/atharva.joshi/Desktop/cdp-mcp`
Scope: 81 tool files (~7k LoC) vs. 12 locally cloned CDP services (~391 controller endpoints) plus additional repos discovered on `acquia` / `agilone` GitHub orgs and Confluence context.
Date: 2026-04-20.

---

## 0. Remediation status (post-audit)

All prioritized items P0 → P3 have been executed. Tool count grew from **~253** (pre-remediation baseline, with predictions/alerts broken) to **286** after P2/P3 landed.

| Pri | Item | Status |
|---|---|---|
| P0‑1 | Predictions mis‑routed to `/{tid}/prediction/predictiondefs` | ✅ Fixed — retargeted to `campaign/predictionDefs`, removed fabricated publish/unpublish/execute tools, fixed clone `action=copy`. |
| P0‑2 | Alerts pointed at a non-existent controller | ✅ Fixed — `register_alert_tools()` is now a no-op until wired to the real MuleSoft/Go Alerts EAPI; legacy impl preserved for reference. |
| P0‑3 | `target_tenant_id: int` on tenants tool | ✅ Fixed — changed to `str`. |
| P1‑A | Auth refresh race + no 401 recovery | ✅ Fixed — `asyncio.Lock` serializes refresh; `get_token(force_refresh=True)` and `invalidate()` added; one‑shot 401 retry in http_client. |
| P1‑B | HTTP client defects (manual query string, no PATCH, no tenant URL-encoding, unclosed client, lost stack traces) | ✅ Fixed — httpx native `params=`, `quote(tenant_id)`, `path.lstrip('/')`, `base_url.rstrip('/')`, PATCH method, DELETE body, per-request timeout override, `logger.exception`, `atexit`-registered client close. |
| P1‑C | Misleading `PathStyle` docstring | ✅ Fixed — `"none"` marked DEPRECATED; `"v2"` and `"bare"` documented against real controllers. |
| P2‑a | Integrate `cdp-mailer-rest-api` | ✅ Done — accounts / subusers / identifiers / batches tool modules registered. |
| P2‑b | Integrate `cdp-emailable-pages-api` | ✅ Done — tool module wired at `/v2/{tenantId}/emailablepages`. |
| P2‑c | Fill missing sub-controllers | ✅ Done — DW profile, workflow step types & mapping scripts, UDMP resources, tenant clusters, orchestration/purge statuses, campaign datasets/files/folders/optimizer/templateDefs/exports, dataset descriptions, dataset def templates, optimizer; provision limits/links verified. |
| P2‑d | Clone + wrap `acquia/cdp-segments-api` | ✅ Done — cloned locally, segments tool module registered. |
| P2‑e | Integration test harness + CI gate | ⚠️ Partial — pytest scaffolding added; full per-service contract tests tracked as follow-up. |
| P3 | Normalize tenant-ID typing | ✅ Done — `find src/cdp_mcp/tools -name "*.py" -exec sed -i …` replaced every `tenant_id: Optional[int]` (238 occurrences across 58 files) with `Optional[str]`; `target_tenant_id: int` → `str`. |
| P3 | Pagination helper | ✅ Done — `HttpClient.paginate(path, page_size=…, max_pages=…, offset_param=…, limit_param=…)` auto‑walks `offset`/`limit` and flattens `{"items"/"results"/"data"/"content": [...]}` payloads. |
| P3 | Structured logging | ✅ Done — every request now emits `CDP <METHOD> <URL> -> <status> (<duration_ms> ms)` via `logger.info`; 401 retry logged at info level; exceptions via `logger.exception` with stack trace. |
| P3 | Bundle `cdp_def_templates` as MCP resource | ❌ Dropped — the repo is a CI/CD scaffolding template (`Dockerfile.ci`, `pipeline.yaml` examples, `pipeline.env`), not JSON definition templates as assumed in §6. Nothing to bundle. Recommend bundling curated campaign/audience/message examples directly into `cdp_mcp/docs/` if a playbook-style resource is desired. |

Final verification: `python3 -c "from cdp_mcp.server import create_server; create_server()"` loads cleanly and `list_tools()` reports **286 tools**.

---

## 1. Executive summary

The MCP covers the bulk of the core CDP Java services (permissions, DW, campaign, config, reports, connectors, cache, security, spam, status, self‑service provisioning). However the audit surfaced one **P0 routing defect** that breaks an entire capability area, a second **P0 defect** in the tenants listing route, a handful of **P1 robustness issues** in the shared HTTP client/auth flow, and several **P2 coverage gaps** where CDP services exist but no MCP tool exposes them (mailer-rest-api, emailable-pages-api, segments-api, plus a few sub‑resource controllers inside campaignapi/configapi/dwapi).

Top 5 things to act on:

1. **P0 — Predictions tool targets a non‑existent URL.** `src/cdp_mcp/tools/predictions/predictions.py` sets `PATH_STYLE="none"` and calls `prediction/predictiondefs`, producing `/{tenantId}/prediction/predictiondefs`. The real controller is `PredictionDefController` in **cdp‑campaignapi** at `/v2/{tenantId}/campaign/predictionDefs` (camelCase). Every prediction lifecycle tool (~10 tools) is currently broken on every environment.
2. **P0 — Alerts tools target a service that doesn't exist on `api.agilone.com`.** `src/cdp_mcp/tools/alerts/alerts.py` uses `PATH_STYLE="none"` and paths like `alertdefs`/`alertdef/{id}`. No `AlertDefController` exists in any cloned `cdp-*` service. CDP Alerts live in the separate MuleSoft/Go stack (`acquia/eee-eapi-cdp-alerts`, `acquia/eee-papi-cdp-alerts`, `acquia/ent-go-eapi-cdp-alerts`), which has its own base URL.
3. **P1 — `http_client.py` docstring is actively wrong** and misled whoever wrote the predictions/alerts modules. Line 23 says `"none"` is used by `campaign, config, connectors, predictions, alerts` — but every inspected controller in campaignapi/configapi is `/v2/{tenantId}/...` (verified: `/v2/{tenantId}/campaign/campaignDefs`, `/v2/{tenantId}/config/connectors`, `/v2/{tenantId}/content/containers`, etc.). The only correct use of `"none"` would have been a legacy CDP API that no longer exists.
4. **P1 — Auth/HTTP robustness.** No token‑refresh lock (race condition under concurrent tool calls), no automatic re‑auth on 401, manual query‑string assembly without URL‑encoding (breaks on special chars in `params`), `body` silently dropped on `PATCH`, `HttpClient.close()` never invoked, stack traces lost via `return failure(str(exc))`.
5. **P2 — Missing service integrations.** `cdp‑mailer‑rest‑api` (4 controllers, 9+ endpoints), `cdp‑emailable‑pages‑api` (6 endpoints), `cdp‑segments‑api` (remote repo), plus several sub‑controllers inside already‑wrapped services (below).

---

## 2. Product context (from Confluence / Acquia docs)

CDP = **Acquia Customer Data Platform** (formerly AgilOne; see Confluence page `agilone/10977404 — Acquia Customer Data Platform (CDP) Product Page`). Per `DEV/57315354 — Feature Teams in Customer Data Platform`, the CDP surface area that this MCP maps to includes:

- CDP Platform + Integration (workflow framework, schedules, connectors, ingest/egress) → `cdp‑configapi`, `cdp‑dwapi`, `cdp‑self‑service‑api`.
- GDPR/CCPA & Data Retention → data‑erasure endpoints in `cdp‑dwapi` + purge status in `cdp‑statusapi`.
- Customer 360 Profiles (API/UI) → `Dw360Controller` + `A360RuleController` + `cdp‑a360` repo.
- Campaigns / Audiences / Messages / Templates → `cdp‑campaignapi` + `cdp_def_templates`.
- Data Quality, Reports & Dashboards → report controllers in `cdp‑campaignapi` + `DwReportController`.
- Predictions & ML → `cdp‑campaignapi/PredictionDefController` + `cdp‑predictions‑api` (content containers/templates).
- Security / Auth / SSO / tokens → `cdp‑security‑service`.
- Mailer identifiers, batches, accounts, sub‑users → `cdp‑mailer‑rest‑api` (**not yet integrated in the MCP**).
- Emailable pages → `cdp‑emailable‑pages‑api` (**not yet integrated**).
- Segments → `acquia/cdp‑segments‑api` (**not yet integrated**).
- Alerts → external MuleSoft/Go service, not an `agilone.com` endpoint (**currently mis‑targeted**).

This mapping is used throughout the coverage matrix below.

---

## 3. Per‑service coverage matrix

Legend: ✅ covered · ⚠️ partial/verify · ❌ missing · 🐞 bug routed wrong.

### 3.1 cdp‑permissions‑api (6 controllers, 21 endpoints)
Base: `/v2/{tenantId}/…`.

| Controller | MCP module | Status |
|---|---|---|
| `RoleController` (`/roles`) | `tools/permissions/roles.py` | ✅ |
| `UserController` (`/users`) | `tools/permissions/users.py` | ✅ |
| `UserLiteController` (`/users-lite`) | `tools/permissions/users_lite.py` | ✅ |
| `SelfServiceRoleController` (`/selfservice-roles`) | `tools/permissions/selfservice_roles.py` | ✅ |
| `SelfServiceUserController` (`/selfservice-users`) | `tools/permissions/selfservice_users.py` | ✅ |
| `BaseController` (no mapping; abstract) | — | n/a |

### 3.2 cdp‑dwapi (14 controllers, 26 endpoints)
Base: `/v2/{tenantId}/dw/…`.

| Controller | MCP | Status |
|---|---|---|
| `DwApiController` + `DwApiActionController` (`/dw/entities/{resourceName}`) | `tools/dw/entities.py` | ✅ |
| `Dw360Controller` (`/dw/a360/{resourceName}`) | `tools/dw/a360.py` | ✅ |
| `DwAudienceController` (`/dw/audienceCount`) | `tools/dw/audience.py` | ✅ |
| `DwTrackerController` (`/{apiVersion}/{tenantId}/dw/tracker` — note `{apiVersion}` is path variable) | `tools/dw/tracker.py` | ⚠️ verify tracker tool passes an apiVersion segment instead of hard‑coding `v2`. |
| `DataErasureStatusController` (`/dw/dataerasurestatus`) | `tools/dw/data_erasure.py` | ✅ |
| `PurgeController` (`/dw/dataerasure`) | `tools/dw/data_erasure.py`? | ⚠️ cross‑check; two controllers, one for erasure initiation, one for status. |
| `DwPurgeController` (`/dw/purge`) | `tools/dw/purge.py` | ✅ |
| `DwOfferApiController` (`/dw/offers`) | `tools/dw/offers.py` | ✅ |
| `DwMetaApiController` (`/dw/resources`) | `tools/dw/metadata.py` | ✅ |
| `DwCampaignMetaApiController` (`/dw/campaign`) | `tools/dw/campaign_meta.py` | ✅ |
| `DwReportController` (`/dw/report/reportDefs`) | `tools/dw/reports.py` | ✅ (verify path includes `/report/`) |
| `DwProfileController` (`/dw/profile`) | — | ❌ **missing tool** — no wrapper for customer profile lookup/fetch. |
| `RTMetaController` (`/dw/rtmeta`) | `tools/dw/rtmeta.py` | ✅ |

### 3.3 cdp‑campaignapi (22 controllers, 133 endpoints)
Base: `/v2/{tenantId}/…` (all controllers).

| Controller | MCP | Status |
|---|---|---|
| `CampaignDefController` (`/campaign/campaignDefs`) | `tools/campaign/definitions.py` | ✅ |
| `AudienceDefController` (`/campaign/audienceDefs`) | `tools/campaign/audiences.py` | ⚠️ Server instructions already note that creating standalone audienceDefs is rejected; tool exists but intentionally discouraged. |
| `MessageDefController` (`/campaign/messageDefs`) | `tools/campaign/messages.py` | ⚠️ same caveat. |
| `DatasetDefController` (`/campaign/datasetDefs`) | `tools/reports/squery_defs.py` or none? | ❌ no dedicated `datasetDefs` tool module. |
| `DatasetDescriptionController` (`/campaign/datasetDescriptions`) | — | ❌ missing. |
| `DatasetDefTemplateController` (`/templates/datasetDefs`) | — | ❌ missing. |
| `FileController` (`/campaign/files`) | — | ❌ missing. |
| `FolderController` (`/campaign/folders`) | — | ❌ missing (needed for organizing campaign artifacts). |
| `OptimizerDefController` (`/optimizer/optimizerdefs`) | — | ❌ missing. |
| `PredictionDefController` (`/campaign/predictionDefs`) | `tools/predictions/predictions.py` | 🐞 **wrong path** — see §4.1. |
| `TemplateDefController` (`/campaign/templateDefs`) | — | ❌ missing (distinct from `TemplateXrefController`). |
| `TemplateXrefController` (`/campaign/templates`) | `tools/campaign/templates.py` | ⚠️ verify module path targets `/campaign/templates`. |
| `ExportDefController` (`/export/dataexport`) | — | ❌ missing. |
| `MimeAttributeController`, `CommonController` | — | ❌ missing (utilities; low priority). |
| `WidgetDefController` (`/report/widgets`) | `tools/reports/widgets.py` | ✅ |
| `SQueryDefController` (`/report/sQueryDefs`) | `tools/reports/squery_defs.py` | ✅ |
| `ReportDefController` (`/report/reportDefs`) | `tools/reports/report_defs.py` | ✅ |
| `DashboardDefController` (`/report/dashboards`) | `tools/reports/dashboards.py` | ✅ |
| `CubicSetDefController` (`/report/cubicSetDefs`) | `tools/reports/cubic_set_defs.py` | ✅ |
| `CubeMetadataController` (`/report/cubeMetadata`) | `tools/reports/cube_metadata.py` | ✅ |
| `CubeStatusController` (`/report/cubeStatus`) | `tools/reports/cube_status.py` | ✅ |

Run/Dispatch/Action sub‑endpoints (inside `CampaignDefController`) — covered via `actions.py`, `dispatches.py`, `runs.py`, `campaign_template_tools.py`. Verify each tool matches the actual sub‑path annotations.

### 3.4 cdp‑configapi (26 controllers, 147 endpoints)

All base paths are `/v2/{tenantId}/config/…` except `TenantController` which is `/v2/config/tenants` (no tenant segment).

| Controller | MCP | Status |
|---|---|---|
| `TenantController` | `tools/config_api/tenants.py` | ⚠️ path correct (`bare` style + `v2/config/tenants`), but `target_tenant_id: int` will fail if tenant IDs are alphanumeric. Use `str`. |
| `WorkflowController` | `tools/config_api/workflows.py` | ✅ |
| `ScheduleController` | `tools/config_api/schedules.py` | ✅ |
| `WorkflowStepTypeController` (`/workflowStepTypes`) | — | ❌ missing. |
| `WorkflowMappingScriptController` (`/workflows/{workflowId}/workflowSteps/{stepId}/mappingScripts`) | — | ❌ missing (sub‑resource, edit workflow step scripts). |
| `UDMPTableController` | `tools/config_api/udmp.py` | ✅ |
| `UDMPResourceController` (`/UDMPResources`) | — | ❌ missing (distinct from UDMPTables). |
| `ClusterController` / `TenantClusterController` | `tools/config_api/clusters.py` | ⚠️ verify both; `TenantClusterController` (`/tenantClusters`) likely missing. |
| `ConnectorController` | `tools/connectors/connectors.py` | ✅ (matches `/v2/{tid}/config/connectors`). |
| `ConnectorDefController` | `tools/connectors/templates.py` (or dedicated module?) | ⚠️ verify. |
| `OutputConnectorController` / `OutputConnectorDefController` | `tools/config_api/output_connectors*.py` | ✅ |
| `A360RuleController` | `tools/config_api/a360_rules.py` | ✅ |
| `MappingTemplateController` | `tools/config_api/mapping_templates.py` | ✅ |
| `CompactionRequestController` | `tools/config_api/compaction_requests.py` | ✅ |
| `ExecutionBucketController` | `tools/config_api/execution_buckets.py` | ✅ |
| `ExecutionSummaryGroupController` | `tools/config_api/execution_summary_groups.py` | ✅ |
| `ValidatorController` (`/columnValidators`) | `tools/config_api/column_validators.py` | ✅ |
| `SchemaCheckpointController` | `tools/config_api/schema_checkpoints.py` | ✅ |
| `EmailController` | `tools/config_api/emails.py` | ✅ |
| `ProvisionerController` | `tools/config_api/provisioning.py` | ✅ |
| `SummaryCustomizationController` | `tools/config_api/summary_customizations.py` | ✅ |
| `DqeP1RuleController` / `DqeP2RuleController` | `tools/config_api/dqe_rules.py` | ⚠️ verify both P1 and P2 paths (`/dqe1Rules`, `/dqe2Rules`). |
| `DatasetDefQueryGeneratorController` (`/config/queryGenerator`) | `tools/config_api/query_generator.py` | ✅ |

### 3.5 cdp‑predictions‑api (2 controllers, 2 endpoints)

Base: `/v2/{tenantId}/content/…`.

| Controller | MCP | Status |
|---|---|---|
| `TemplateController` (`/content/templates`) | `tools/predictions/content.py` | ✅ |
| `ContainerController` (`/content/containers`) | `tools/predictions/content.py` | ✅ |

The **prediction lifecycle** (`tools/predictions/predictions.py`, 10 tools) is *not* served by this service — it belongs to `cdp‑campaignapi/PredictionDefController` and is currently mis‑routed (§4.1).

### 3.6 cdp‑security‑service (4 controllers, 13 endpoints)

Bare paths (no tenant, no /v2): `/token`, `/authentication`, `/authentication/reset`, `/sso`.

| Controller | MCP | Status |
|---|---|---|
| `TokenController` (`/token`) | `tools/security/auth.py` | ✅ — bypasses `http_client` and builds URL from `base_url` directly. Matches `RESOURCE_TOKEN = "/token"`. |
| `AuthenticationController` (`/authentication`) | `tools/security/auth.py` | ⚠️ verify `/authentication/session` — not visible in `AuthenticationController.java` via grep; may have been renamed or removed. Test or inspect controller in full. |
| `AuthenticationResetController` (`/authentication/reset`) | `tools/security/password_reset.py` | ✅ — actions `generate`, `validate`, `update` match controller. |
| `SsoController` (`/sso`) | `tools/security/sso.py` | ✅ |

Also note: `auth_provider.py` uses `/token?action=create` with all credentials in **headers**, per securityAPI spec. Good.

### 3.7 cdp‑cacheapi (1 controller, 9 endpoints)

Base: `/v2/{tenantId}/cache`.
MCP paths (`cache/{type}/key/{k}`, `cache/{type}/id/{id}`, `cache/{type}/group/{g}/id/{id}` × GET/PUT/DELETE) exactly match `CacheController` — ✅ 9/9.

### 3.8 cdp‑statusapi (3 controllers, 7 endpoints)

| Controller | MCP | Status |
|---|---|---|
| `StatusApiController` (`/status/{resourceType}`) | `tools/status/status.py` calling `status/statusmessage` | ⚠️ path maps `{resourceType}=statusmessage`. Confirm that is a supported resource type. If dynamic, expose `resource_type` as a tool parameter. |
| `OrchestrationStatusController` (`/orchstatus`) | — | ❌ missing. |
| `DataPurgeStatusController` (`/purgestatus`) | — | ❌ missing (duplicates dwapi `dataerasurestatus` from a different angle). |

### 3.9 cdp‑spam‑score‑api (1 endpoint)

`SpamScoreController` (`/v2/{tenantId}/spam/score`) ↔ `tools/spam/spam.py` — ✅. Server instructions correctly flag that body must be a JSON **array**.

### 3.10 cdp‑self‑service‑api (4 controllers, 17 endpoints)

`ProvisionServiceController`, `ProvisionServiceInstanceController`, `ProvisionConnectorLinkController`, `ProvisionServiceLimitController` — mostly covered via `tools/provisions/provisions.py` and `tools/config_api/provisioning.py`.
⚠️ `ProvisionServiceLimitController` (`/provisions/limits`) and `ProvisionConnectorLinkController` (`/provisions/links`) need explicit verification — grep shows only `provisions/services` and `provisions/instances` in the MCP tool.

### 3.11 cdp‑mailer‑rest‑api (6 controllers, 9+ endpoints) — ❌ **not integrated**

`MailerAccountController`, `MailerSubUserController`, `MailerIdentifierController`, `MailerBatchController` (+2 abstracts). None of them have MCP tools.

### 3.12 cdp‑emailable‑pages‑api (1 controller, 6 endpoints) — ❌ **not integrated**

`EmailablePagesController` (`/v2/{tenantId}/emailablepages`) — absent from MCP.

### 3.13 Alerts — target service not local

See §4.2. The MCP alert tools point at `{agilone‑base‑url}/{tid}/alertdefs` which does not exist. The real Alerts API lives outside the `agilone.com` domain.

---

## 4. Bugs

### 4.1 🔴 P0 — Predictions tools mis‑routed

File: `src/cdp_mcp/tools/predictions/predictions.py`
- `PATH_STYLE = "none"` → URLs skip `/v2/` prefix.
- Base path `prediction/predictiondefs` (lower‑case `defs`) does not exist anywhere.
- Effective URL: `https://{env}.agilone.com/{tid}/prediction/predictiondefs` → **404** on every call.
- Correct target is `PredictionDefController` in `cdp‑campaignapi` at `/v2/{tenantId}/campaign/predictionDefs` (note camel‑case `predictionDefs`).

Fix: delete the `PATH_STYLE` override, change path template to `campaign/predictionDefs` (default `v2` style), rename tools or documentation to reflect they belong to Campaign API. Affected tools: `cdp_list_predictions`, `cdp_list_published_predictions`, `cdp_get_prediction`, `cdp_create_prediction`, `cdp_update_prediction`, `cdp_delete_prediction`, `cdp_publish_prediction`, `cdp_unpublish_prediction`, `cdp_execute_prediction`, `cdp_clone_prediction` (~10).

### 4.2 🔴 P0 — Alerts tools target a non‑existent endpoint

File: `src/cdp_mcp/tools/alerts/alerts.py`
- No `AlertDefController` exists in any cloned `cdp-*` service.
- GitHub search on `org:acquia` shows Alerts are delivered through the MuleSoft/Go stack (`eee-eapi-cdp-alerts`, `eee-papi-cdp-alerts`, `ent-go-eapi-cdp-alerts`, `ent-go-papi-cdp-alerts`), whose base URLs differ from `*.agilone.com`.
- The historical in‑platform `alertdefs` endpoint referenced by `apiSpecification/specs/alertAPI.json` (per the module docstring) appears to have been retired.

Fix options:
1. Remove alert tools until the target is clarified.
2. Add a separate base‑URL + auth config for the Alerts EAPI/PAPI and rewrite tools against that spec.

### 4.3 🔴 P0 — `cdp_get_tenant` / `cdp_list_tenants` parameter type

File: `src/cdp_mcp/tools/config_api/tenants.py:39`
```python
async def cdp_get_tenant(target_tenant_id: int) -> str:
```
Tenant IDs returned by `TenantController` are often non‑numeric (GUIDs/slugs). Declaring `int` will cause MCP schema validation to reject legitimate inputs. Change to `str | int` or `str`.

### 4.4 🟠 P1 — `http_client.py` path‑style documentation is wrong

File: `src/cdp_mcp/utils/http_client.py:23`
```python
#   "none":          /{tenantId}/...     (used by campaign, config, connectors, predictions, alerts)
```
Every campaign/config/connector controller actually lives under `/v2/{tenantId}/…`. This comment caused the predictions bug and will cause repeats. Update it — `none` should only be documented for legacy/none‑existent APIs, or delete the style entirely.

### 4.5 🟠 P1 — Auth refresh race / missing 401 retry

File: `src/cdp_mcp/auth/auth_provider.py`
- Concurrent tool calls after token expiry can each trigger `_refresh_token()` (5+ simultaneous `POST /token?action=create`). Add an `asyncio.Lock`.
- If the server rotates/rejects a token early, the MCP still returns the cached token. `http_client.request` should trap `401 Unauthorized` and retry once after `_refresh_token()` (bypassing the 60 s buffer).

### 4.6 🟠 P1 — Manual query‑string assembly is not URL‑encoded

File: `src/cdp_mcp/utils/http_client.py:81‑87`
```python
query_string = "&".join(f"{k}={v}" for k, v in filtered.items())
```
Any `v` containing `&`, `=`, spaces, or `?` produces an invalid URL (e.g., `q="name=foo bar"`). Use `httpx.QueryParams` or pass `params=` through to `client.request(...)`.

### 4.7 🟠 P1 — Body dropped on `PATCH` / `DELETE`

File: `src/cdp_mcp/utils/http_client.py:132`
```python
json=body if body is not None and method in ("POST", "PUT") else None,
```
Should include `"PATCH"` (and `"DELETE"` for the handful of CDP endpoints that accept a body — e.g., some bulk‑delete actions). Adds a silent failure mode.

### 4.8 🟠 P1 — Shared `httpx.AsyncClient` never closed

`HttpClient._client` is created lazily; `close()` exists but no caller invokes it. Register a shutdown hook via `FastMCP` lifecycle or `atexit` so the connection pool is cleanly torn down.

### 4.9 🟠 P1 — Errors lose their stack trace

`except Exception as exc: return failure(str(exc))` silently discards traceback. At minimum log it (e.g., `logger.exception(...)`). Ideally wrap httpx exceptions in a typed `CDPError`.

### 4.10 🟡 P2 — No leading‑slash normalization

`_build_url` concatenates `{tid}/{path}`. If any tool accidentally passes `/cache/...`, the URL becomes `…/{tid}//cache/...`. Add `path = path.lstrip("/")`.

### 4.11 🟡 P2 — `_build_url` does not URL‑encode `tenant_id`

If the tenant identifier ever contains a space/non‑ASCII character, the URL is silently malformed. Run it through `urllib.parse.quote`.

### 4.12 🟡 P2 — Inconsistent parameter typing across tools

`tenant_id` is `Optional[int]` in some tool modules (e.g., `predictions.py`) and `Optional[str | int]` in others. Pick one canonical type (recommend `Optional[str]`) so the generated MCP schema is consistent.

### 4.13 🟡 P2 — `DwTrackerController` uses `{apiVersion}` path variable

The controller is `/{apiVersion}/{tenantId}/dw/tracker`, meaning the API version is routable (clients can pin `v1` or `v2`). The MCP tracker tool should expose `api_version` (default `v2`) rather than hard‑code.

### 4.14 🟡 P2 — `cdp_get_status` resource type hard‑coded to `statusmessage`

`StatusApiController` path is `/v2/{tenantId}/status/{resourceType}`. `tools/status/status.py` hard‑codes `statusmessage`. Convert `resource_type` into a required tool param, or expose sibling tools per known resource type.

---

## 5. Enhancements & missing coverage

### 5.1 Integrate missing services

| Service / repo | Notes |
|---|---|
| `cdp-mailer-rest-api` (local) | Add tools for `/mailer/accounts`, `/mailer/subusers`, `/mailer/identifiers`, `/mailer/batches`. Batches require a POST‑by‑id workflow. |
| `cdp-emailable-pages-api` (local) | 6 endpoints under `/v2/{tenantId}/emailablepages`. |
| `acquia/cdp-segments-api` (remote) | Segment definitions — not yet cloned. Clone and add segments tool module. |
| `acquia/cdp-a360` (remote) | May overlap with DW `Dw360Controller` but exposes indexing/search not in `cdp-dwapi`. Check before duplicating. |
| Alerts (MuleSoft / Go) | `acquia/eee-eapi-cdp-alerts`, `eee-papi-cdp-alerts`, `ent-go-eapi-cdp-alerts`. Requires separate base URL and likely a different auth scheme. |

### 5.2 Missing controllers inside services already wrapped

- **cdp-dwapi**: `DwProfileController` (`/dw/profile`) — profile lookups.
- **cdp-configapi**: `WorkflowStepTypeController`, `WorkflowMappingScriptController` (nested under workflows), `UDMPResourceController`, `TenantClusterController`.
- **cdp-campaignapi**: `DatasetDefController`, `DatasetDescriptionController`, `DatasetDefTemplateController`, `FileController`, `FolderController`, `OptimizerDefController`, `TemplateDefController`, `ExportDefController`.
- **cdp-statusapi**: `OrchestrationStatusController`, `DataPurgeStatusController`.
- **cdp-self-service-api**: confirm `/provisions/limits` and `/provisions/links` are wrapped.

### 5.3 Quality / DX improvements

- **Schema validation** on `body` JSON: most `body: str` tools silently pass malformed JSON to the server. Validate `json.loads(body)` up‑front and return a clean error.
- **Pagination helpers**: most list endpoints take `offset`/`limit`; add a generic `paginate=true` flag that auto‑fetches pages until empty.
- **Testing**: there is no `tests/` directory. Add contract tests that hit a mock/stub server per service to catch routing regressions (the predictions bug would have been caught by a single integration test).
- **Tool count discipline**: server.py registers 150+ tools. Consider grouping rarely‑used ones behind a single `cdp_exec` meta‑tool to reduce cognitive load in clients with tool‑count limits.
- **Replace the static ``"Endpoint unsupported"`` note** in `server.py` instructions for `cdp_create_audience_def` with a deprecation stub that returns the message, so callers discover it via the normal tool surface.
- **`docs/` + `resources/` coverage**: the `campaign-playbook` resource is referenced; make sure analogous playbooks exist for DW, Reports, and Provisions.
- **Env config**: `base_url` strips no trailing `/`. A `.env` with `CDP_BASE_URL_DEV=https://dev-api6.agilone.com/` would produce `//v2/{tid}/...`. Normalize.
- **Logging**: add structured logging of request method, URL, status code, duration — invaluable for field‑debugging from MCP clients.

### 5.4 Suggested internal improvements to `http_client.py`

- Remove `path_style="none"` entirely; no service uses it.
- Replace manual query string with httpx's native `params=`.
- Add `PATCH` and `OPTIONS` to the supported method list.
- Support per‑request timeout overrides (some DW `execute` endpoints run long).
- Return typed `CDPSuccess` / `CDPError` dataclasses rather than a `dict`.

---

## 6. Repositories discovered on GitHub that may be relevant

Found on `acquia` org (search: `cdp- org:acquia in:name`):

| Repo | Relevance |
|---|---|
| `acquia/cdp-segments-api` | Segments API — **missing integration**. |
| `acquia/cdp-a360` | A360 indexing — overlap with DW; evaluate. |
| `acquia/cdp-ai-tools` | AI tooling — may inspire additional MCP tools (out of scope for remediation). |
| `acquia/eee-eapi-cdp-alerts`, `eee-papi-cdp-alerts`, `ent-go-eapi-cdp-alerts`, `ent-go-papi-cdp-alerts` | Real Alerts APIs — see §4.2. |
| `acquia/cdp-alerts-ticket`, `cdp-alert-ticket-tool` | Salesforce ticket bridges; probably not MCP targets. |
| `acquia/CDP-Platform-Orchestration`, `cdp-databricks-workflow`, `cdp-infrastructure-automation`, `cdp-ops-portal`, `cdpbot` | Internal infra / IaC / Slack bot — not MCP targets. |
| `acquia/cdp_def_templates` | **Not useful** for an MCP resource — on inspection, the repo is a CI/CD scaffolding template (Dockerfile.ci, pipeline.yaml examples, pipeline.env). It contains no JSON campaign/audience/message defs. |

No unexpected `cdp-*` controller repos on `agilone` org (which was absorbed into Acquia).

---

## 7. Prioritized action list

| # | Pri | Action | Status |
|---|---|---|---|
| 1 | P0 | Fix `tools/predictions/predictions.py`: drop `PATH_STYLE`, retarget to `campaign/predictionDefs`. Add test. | ✅ |
| 2 | P0 | Decide fate of `tools/alerts/alerts.py` — remove or retarget to the MuleSoft/Go Alerts EAPI (needs separate base URL & auth). | ✅ (disabled; awaiting separate Alerts stack integration) |
| 3 | P0 | Change `cdp_get_tenant` / `cdp_list_tenants` tenant ID type from `int` to `str`. | ✅ |
| 4 | P1 | Rewrite `http_client.py`: use `httpx` native `params=`, add `PATCH` support, strip leading `/`, quote tenant ID, strip trailing `/` from base_url, register close handler, add `asyncio.Lock` around token refresh, retry once on 401. | ✅ |
| 5 | P1 | Correct the misleading `PathStyle` docstring in `http_client.py`. | ✅ |
| 6 | P2 | Integrate `cdp-mailer-rest-api` and `cdp-emailable-pages-api`. | ✅ |
| 7 | P2 | Fill in the missing sub‑controllers (workflow step types & scripts, UDMP resources, tenant clusters, orchestration/purge statuses, DW profile, campaign datasets/files/folders/optimizer/template/export). | ✅ |
| 8 | P2 | Add `cdp-segments-api` (clone + wrap). | ✅ |
| 9 | P2 | Introduce an integration test harness per service; gate CI on it. | ⚠️ partial (scaffolding only) |
| 10 | P3 | Normalize tenant‑ID typing across tools; add pagination helper; add structured logging; bundle `cdp_def_templates` as an MCP resource. | ✅ typing / ✅ pagination / ✅ logging / ❌ templates bundle (repo is CI scaffolding, not JSON defs — recommendation revised) |

---

## 8. Appendix — raw endpoint inventory

Per‑service counts extracted from controller annotations (`/tmp/cdp-audit/endpoints.json`):

```
cdp-cacheapi:            1 controllers,   9 endpoints
cdp-campaignapi:        22 controllers, 133 endpoints
cdp-configapi:          26 controllers, 147 endpoints
cdp-dwapi:              14 controllers,  26 endpoints
cdp-emailable-pages-api: 1 controllers,   6 endpoints
cdp-mailer-rest-api:     6 controllers,   9 endpoints
cdp-permissions-api:     6 controllers,  21 endpoints
cdp-predictions-api:     2 controllers,   2 endpoints
cdp-security-service:    4 controllers,  13 endpoints
cdp-self-service-api:    4 controllers,  17 endpoints
cdp-spam-score-api:      1 controllers,   1 endpoints
cdp-statusapi:           3 controllers,   7 endpoints
                       ——— total ———    391 endpoints
```

Full per‑controller base paths: see `3` coverage matrix.

---

## 11. UI-pattern enhancements (ui-vega + ui-config `2601-release`)

Following the user's request to identify sequencing patterns from the
customer-facing Vega UI and admin Config UI, the following tools were
added or corrected. Total tool count: **286 → 297**.

### 11.1 Fixed contracts

| Tool | Bug before | Fix (UI-verified) |
|------|------------|-------------------|
| `cdp_start_campaign` | Sent no body → `E400` on current CDP builds | Always sends `{"campaignProperties":"{}"}` (matches `campaign-data.service.ts` `runCampaign`). `cohort` retyped `Optional[bool]` serialized as `true`/`false`. |
| `cdp_create_campaign` / `cdp_update_campaign` | `folderId` not supported | Added `folder_id: Optional[int]` — Vega sends `?folderId=` on every save. |
| `cdp_run_workflow` | No body param → triggered workflows rejected | Added optional `body: str` (JSON) — required for `*_FLOW_DEFAULT` workflows. |

### 11.2 New tools

| Tool | Backend | Sourced from |
|------|---------|--------------|
| `cdp_publish_web_campaign` | `POST config/workflows/CAMPAIGN_FLOW_DEFAULT?action=run` body `{"campaignProperties":"{\"webAction\":\"PUBLISH\"}"}` | Vega `campaign-data.service.ts` `publishCampaign` |
| `cdp_copy_datasetdef` | `POST campaign/datasetDefs/{id}?action=copy` | Vega comment: canonical recovery for shared-datasetDef E400 |
| `cdp_list_data_exports` / `cdp_get_data_export` / `cdp_create_data_export` / `cdp_update_data_export` / `cdp_delete_data_export` / `cdp_copy_data_export` | `export/dataexport` CRUD + `?action=copy` | Vega `dataExport.service.ts`; closes §5.1 `ExportDefController` gap |
| `cdp_run_data_export` | `POST config/workflows/DATA_EXPORT_DEFAULT?action=run&entityType=exportDef` body `{"dataExportProperties":"{}"}` | Vega `dataExport.service.ts` `runExport` |
| `cdp_list_dataset_defs` / `cdp_get_dataset_def` | `campaign/datasetDefs` read | `DatasetDefController` — enables inspect-before-copy flow |

### 11.3 Documentation

`src/cdp_mcp/docs/campaign_playbook.md` extended with section **"UI-derived
orchestration patterns"** covering:

1. `folderId` always-pass rule
2. Batch vs. triggered publish distinction
3. Shared-datasetDef E400 recovery
4. Data-export save-then-run flow
5. Async audience-sizing polling loop
6. Generic workflow invocation with body
7. Full Vega campaign-wizard lifecycle as a seven-step recipe

### 11.4 Verification

```
$ python3 -c "from cdp_mcp.server import create_server; import asyncio; \
    print(len(asyncio.run(create_server().list_tools())))"
297
```

All 12 new/modified tools registered and discoverable by MCP clients.

---

## 12. UI-derived playbooks (round 2)

Deeper review of `ui-vega` + `ui-config` (`2601-release`) surfaced several multi-step
flows the single-tool MCP calls cannot cover on their own. Three new authoritative
playbooks were authored and four new tools filled gaps in the schedule / workflow
surface. Tool count **297 → 301**.

### 12.1 New tools

| Tool | Backend | Sourced from |
|------|---------|--------------|
| `cdp_invoke_workflow_action` | `POST config/workflows/{name}?action=<verb>&entityType=…&entityId=…&scheduleId=…` | Generic escape hatch observed everywhere in Vega/Config: `ConnectorDataService` (action=publish/schedule/unschedule), `StatusController` (action=rerun/kill on jobs), `ScheduleService` (action=activate_schedule/deactivate_schedule). The existing `cdp_run_workflow` hard-coded `action=run`. |
| `cdp_create_schedule` | `POST config/schedules` | `ScheduleService.createSchedule` — canonical body shape documented. |
| `cdp_update_schedule` | `PUT config/schedules/{id}` | `ScheduleService.updateSchedule`. |
| `cdp_delete_schedule` | `DELETE config/schedules/{id}` | `ScheduleService.deleteSchedule` — paired with an `unschedule` workflow action (see orchestration playbook §1.3). |

Previously the MCP only exposed list/get + activate/deactivate schedule tools; the
create/update/delete path was absent despite being the single most common admin
operation (connector schedules, report schedules, export schedules).

### 12.2 New playbooks

| Resource URI | Scope |
|--------------|-------|
| `cdp://docs/orchestration-playbook` | Generic schedule lifecycle; connector / report / data-export / campaign send-now & scheduled runs; sQueryDef generate→validate→save; provisioner workflow; compaction; job control; drain-before-delete rule; universal "fetch runner → POST definition → POST action verb → poll" decomposition. |
| `cdp://docs/customer360-playbook` | Three-parallel-fetch retrieval (`dw/a360/customers` + `UDMPTables` + two tenant 360 layout properties); layout deep-merge rules (`udmColumn`, `overwriteAtIndex`, `mergeAtIndex`); realtime polling with `If-Modified-Since`; `targetentity` pagination; `fq` advanced-search encoding; GDPR identity purge polling; A360 rule validation; minimum tool set to faithfully render a profile. |
| `cdp://docs/admin-ops-playbook` | DQE batch writes with dry-run-via-compaction; A360 three-phase saves (creates → updates → deletes); compaction lifecycle; Status-page job control (rerun/kill/suspend/resume) with `entityTypeMap` verb routing; GDPR erasure flow and admin override; provisioner package runs; content-model bulk `templates/provision?action=update`; user/role onboarding order; universal drain-before-delete rule. |

Each playbook is declared as an MCP resource with an agent-facing description that
includes the exact tool names it governs — clients discover them the same way they
discover the campaign playbook.

Server-level `instructions` updated to point to all four playbooks.

### 12.3 Verification

```
$ python3 -c "from cdp_mcp.server import create_server; import asyncio; \
    s = create_server(); \
    print('tools:', len(asyncio.run(s.list_tools()))); \
    print('doc resources:', sum(1 for r in asyncio.run(s.list_resources()) if 'docs' in str(r.uri)))"
tools: 301
doc resources: 4
```

---

## 13. UI-derived playbooks (round 3)

A third pass across `ui-vega/src/app/main/reports/**`,
`ui-vega/src/app/main/dashboard/**`, `ui-core/src/app/services/workflow/**`,
`ui-core/src/app/services/connector/**`, `ui-config/src/app/main/connector/**`,
`ui-config/src/app/main/udmp/**`, `ui-config/src/app/main/mapping-templates/**`,
`ui-config/src/app/main/content-models/**`, and
`ui-config/src/app/main/tenantProperties/**` uncovered four additional
multi-step flows that single-tool MCP calls cannot encode. Four new
playbooks were authored; no new tools were required (the existing surface is
already sufficient once sequenced correctly).

### 13.1 New playbooks

| Resource URI | Scope |
|--------------|-------|
| `cdp://docs/reports-dashboards-playbook` | Array-wrap POST contract for `reportDefs` / `dashboards`, mandatory `?folderId=` query param, `REPORT_RUNNNER_DEFAULT` triple-N send-now workflow, cube metadata walk (`cubemetadata` → `dimensions` → `hierarchies` → `levels`), ad-hoc execute (`?action=execute`, `cubicSetDef.model` stringified JSON) vs cached fetch (`?action=fetch`), `cubeStatus?cubes=["..."]` JSON-array query param, `BI_MAPPER_DEFAULT` + `A1_ORCHESTRATOR` dual freshness check, `uiProperties` JSON-string layout serialization, dashboard N+1 widget materialization, multi-report attribute-schema compatibility check, sQueryDef argument validation and UDMP resource binding. |
| `cdp://docs/workflow-authoring-playbook` | Symbolic `workflowId` vs numeric `workflowDBId` identifier split (URL segment vs `entityId` query param — #1 invocation bug), three-parallel-GET graph load (`workflows/{id}` + `/workflowSteps` + `/workflowEdges`) with consistent `version` param, versioning rules (query-string only on `deploy`/`delete`, PUT always writes the draft), batch step POST/PUT (single array call) vs per-script parallel POST/PUT/DELETE for mapping scripts, single-POST edges replacement semantic, full create→steps→edges→deploy sequence, invocation verb taxonomy (`run`, `deploy`, `schedule`, `unschedule`, `activate_schedule`, `rerun`, `kill`, `publish`), drain-before-delete rule, system workflow directory (`AIF_RUNNER`, `CONNECTOR_OPS_DEFAULT`, `CAMPAIGN_FLOW_DEFAULT`, `REPORT_RUNNNER_DEFAULT`, `DATA_EXPORT_DEFAULT`, `PROVISIONER_TOOL_DEFAULT`, `BI_MAPPER_DEFAULT`, `A1_ORCHESTRATOR`, `AIF_TENANT_PROVISIONER`). |
| `cdp://docs/connector-wizard-playbook` | Input vs output endpoint swap (`connectors` vs `outputConnectors`, `connectorDefs` vs `outputConnectorDefs`), the 4-or-5-step wizard with `ssidPrefix`-based branching, verbatim `inputConnectorsToSkip` and `intervalConnectors` constants, create → `CONNECTOR_OPS_DEFAULT?action=publish` two-step, the 3-step schedule orchestration (`GET AIF_RUNNER` for numeric id → `POST schedules` with `referenceId=<aifRunnerId>` and `entityId=<connectorId>` → `POST AIF_RUNNER?action=schedule&scheduleId=<sid>`) and its `referenceId` vs `entityId` trap, reverse 2-step unschedule-then-delete, `[entity, [columns]]` mapping tuple shape with UI-decoration strip rule, parameter completion rule (merge `connectorDef.parameters` into connector body), `dateStarted` epoch-millis requirement to avoid first-run full-scan, increment-uniqueness validation. |
| `cdp://docs/udmp-metadata-playbook` | Nested `{columns: {content: []}}` read shape vs flat `{columns: []}` write shape (and the flatten-before-write / nest-on-error pattern), parallel POST/PUT/DELETE `saveResources` batch semantics (non-transactional, no bulk endpoint), the `UDMPTables → UDMPResources` cascade that the MCP does not auto-orchestrate, schema publish ordering (pause cube/SQL consumers and unpublish input connectors first), `unPublished` flagging via `schemaColumnIncrement`, custom-attribute whitelist gate (`UDM+` / `summaryEntity.customAttribute.whitelist`), idempotent PUT `UDMPTables/{tid}/tableoverrides` upsert, column-validator batch save, `mappingTemplates` FK-to-connector precheck, the unusual `PUT campaignAPI templates/provision?action=update` contract (PUT + action query + non-array body), `customer360 / default.360.layout` read-only protection for non-default tenants + `tenant.360.layout` override path, `propertyGroup` taxonomy. |

### 13.2 Verification

```
$ python3 -c "from cdp_mcp.server import create_server; import asyncio; \
    s = create_server(); \
    print('tools:', len(asyncio.run(s.list_tools()))); \
    print('doc resources:', sum(1 for r in asyncio.run(s.list_resources()) if 'docs' in str(r.uri)))"
tools: 301
doc resources: 8
```

Tool count unchanged (301) — this round was pure documentation.
Playbook resources doubled from 4 to 8. Server `instructions` block updated
to reference all eight playbook URIs so MCP clients discover the full set on
connect.


