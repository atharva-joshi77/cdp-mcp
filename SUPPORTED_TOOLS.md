# Supported Tools

This document lists every tool the `cdp-mcp` server registers with MCP clients. **Total: 301 tools** across 16 CDP service areas.

Every tool accepts an optional `tenant_id` parameter. When omitted, the server falls back to the `CDP_TENANT_ID` set in your environment / `.env` file.

> Tool names are the identifiers MCP clients display in their tool picker. Descriptions shown below are the one-liners exposed to the LLM to help it pick the right tool. For parameter-level detail, inspect the tool via MCP Inspector or read the source under `src/cdp_mcp/tools/`.

## Contents

- [Permissions — users, roles, clients](#permissions) — 25 tools
- [Data Warehouse — entities, A360, audiences, offers, trackers, purge](#dw) — 28 tools
- [Campaigns — definitions, audiences, messages, dispatches, runs, exports, templates](#campaign) — 41 tools
- [Config API — tenants, workflows, schedules, UDMP, DQE, clusters, connectors, mappings](#config-api) — 75 tools
- [Connectors — input/output connectors and connector templates](#connectors) — 10 tools
- [Reports & Query — dashboards, widgets, cubes, sQueryDefs, report defs](#reports) — 37 tools
- [Predictions & Content — prediction defs, templates, containers](#predictions) — 8 tools
- [Mailer — accounts, subusers, identifiers, batches](#mailer) — 2 tools
- [Emailable Pages](#emailable-pages) — 6 tools
- [Security — token, authentication, SSO, password reset](#security) — 11 tools
- [Cache operations](#cache) — 9 tools
- [Spam score](#spam) — 1 tools
- [Status — job status, orchestration, purge](#status) — 6 tools
- [Self-Service Provisioning](#provisions) — 17 tools
- [Global platform actions](#global-actions) — 3 tools
- [Query](#query) — 2 tools

## Permissions — users, roles, clients

<a id="permissions"></a>

| Tool | Description |
|------|-------------|
| `cdp_create_client` | Create a new OAuth client. Requires client_id_str, client_secret, grants, and token_validity. |
| `cdp_create_role` | Create a new role with whitelist/blacklist permissions. Pass whitelist/blacklist as JSON arrays of Permission objects. |
| `cdp_create_selfservice_user` | Create a new self-service user. Pass user details as a JSON string. |
| `cdp_create_user` | Create a new CDP user. Requires userName and password. |
| `cdp_delete_client` | Delete an OAuth client by numeric ID |
| `cdp_delete_role` | Delete a role by ID |
| `cdp_delete_selfservice_user` | Delete a self-service user by ID |
| `cdp_delete_user` | Delete a CDP user by ID |
| `cdp_get_client` | Get a specific OAuth client by numeric ID |
| `cdp_get_role` | Get a specific role by ID |
| `cdp_get_selfservice_user` | Get a specific self-service user by ID |
| `cdp_get_user` | Get a specific CDP user by ID |
| `cdp_get_user_lite` | Get a specific user in lightweight format by ID |
| `cdp_list_clients` | List all OAuth clients for a tenant |
| `cdp_list_role_actions` | List all available permission actions that can be assigned to roles |
| `cdp_list_roles` | List all roles for a CDP tenant. Supports optional search and tenantIds (comma-separated string, e.g. '0,425,802') for multi-tenant queries. |
| `cdp_list_selfservice_roles` | List available self-service roles for a tenant |
| `cdp_list_selfservice_users` | List all self-service users for a tenant |
| `cdp_list_users` | List all CDP users for a tenant with pagination; optional search filter |
| `cdp_list_users_lite` | List all users in lightweight format (fewer fields, faster response) |
| `cdp_update_client` | Update an existing OAuth client |
| `cdp_update_role` | Update an existing role. Pass whitelist/blacklist/included as JSON strings. |
| `cdp_update_selfservice_user` | Update a self-service user. Pass updated fields as a JSON string. |
| `cdp_update_selfservice_user_status` | Update a self-service user's status (e.g., activate/deactivate). Pass action and body as JSON string. |
| `cdp_update_user` | Update an existing CDP user's details |

## Data Warehouse — entities, A360, audiences, offers, trackers, purge

<a id="dw"></a>

| Tool | Description |
|------|-------------|
| `cdp_calculate_audience` | Start an asynchronous audience count calculation. Returns a jobId to poll with cdp_get_calculated_count. Pass segment definition as a JSON string. |
| `cdp_create_entity` | Create a new entity in a DW resource. Pass entity data as a JSON string. |
| `cdp_data_erasure_status_override` | Admin-only: override the status of a data erasure request (POST /dw/dataerasure/admin?action=statusoverride). Pass override payload as JSON string. |
| `cdp_delete_data_erasure_request` | Cancel/delete a pending data erasure request |
| `cdp_describe_entity` | Get the schema/attribute definitions for a DW entity resource |
| `cdp_describe_resources` | List all available DW resources (tables/entities) for a tenant |
| `cdp_dw_execute_report` | Execute a report in real-time via the DW API path. Pass report definition as a JSON string. |
| `cdp_dw_fetch_report` | Fetch cached report results via the DW API path |
| `cdp_get_audience_count` | Get audience count based on a segment definition (synchronous). Pass segment definition as a JSON string. |
| `cdp_get_calculated_count` | Get the result of an async audience calculation (poll after cdp_calculate_audience) |
| `cdp_get_campaign_output_attributes` | Get the output attribute columns for a campaign definition. Pass campaign definition as a JSON string. |
| `cdp_get_customer_360` | Get Customer 360 summary view for a resource type (e.g., list of customer profiles) |
| `cdp_get_customer_360_detail` | Get detailed Customer 360 profile for a specific customer |
| `cdp_get_customer_360_realtime` | Get real-time Customer 360 data (includes latest streaming events) |
| `cdp_get_customer_identities` | Get all identities associated with given customer IDs. Pass customer IDs as a JSON string body. |
| `cdp_get_data_erasure_status` | List all data erasure request statuses for a tenant |
| `cdp_get_data_erasure_status_by_id` | Get the status of a specific data erasure request by resource ID |
| `cdp_get_entity` | Get a single entity by its resource name and ID |
| `cdp_get_offers` | Retrieve available offers for a customer or segment. Pass offer request as a JSON string. |
| `cdp_list_entities` | Query entities from a CDP data warehouse resource (e.g., customer, organization, transaction). Supports filtering via fq parameter. |
| `cdp_lookup_values` | Lookup distinct values for a field in a DW entity resource. Requires the field name to look up. Pass lookup request as JSON string. |
| `cdp_post_tracking_event` | Post a real-time tracking event to the CDP (POST /{apiVersion}/{tenantId}/dw/tracker). api_version is a routable path segment — defaults to 'v2' but the controller accepts any version clients want to pin. Pass event d... |
| `cdp_purge_data` | Purge customer data from the data warehouse. Pass purge request as a JSON string with customerIds, purgeReason, and optional purgeTypes. |
| `cdp_refresh_rtmeta` | Refresh the real-time metadata switch values. Must be called with tenantId=0. |
| `cdp_request_data_erasure` | Request GDPR/CCPA data erasure for a customer (by identityHash or email). Pass erasure request as a JSON string. |
| `cdp_update_customer_profile` | Update customer profile attributes in real-time (POST /v2/{tenantId}/dw/profile). Pass profile update data as a JSON string. |
| `cdp_update_data_erasure_request` | Update an existing data erasure request (PUT /dw/dataerasure). Pass the updated erasure request body as a JSON string. |
| `cdp_update_entity` | Update an existing entity in a DW resource. Pass updated fields as a JSON string. |

## Campaigns — definitions, audiences, messages, dispatches, runs, exports, templates

<a id="campaign"></a>

| Tool | Description |
|------|-------------|
| `cdp_clone_campaign` | Clone/copy a campaign definition by ID. Creates a duplicate. |
| `cdp_copy_data_export` | Copy/duplicate a data export definition by ID. |
| `cdp_copy_datasetdef` | Copy an existing datasetDef (audience definition) to create a new, independent one. CDP rejects shared datasetDefs across campaigns with E400: 'The campaignDef being created refers to an existing datasetDef. Please co... |
| `cdp_create_audience_def` | Create a new audience definition. WARNING: the underlying endpoint POST /campaign/audienceDefs is NOT supported on current CDP builds and will return E400 'Request method POST is not supported'. Instead, define the au... |
| `cdp_create_campaign` | Create a new campaign definition. Recommended workflow: call with name+description ONLY to get a resourceId, then call cdp_update_campaign with the full body containing INLINE 'audience' and INLINE 'messageDefs' objec... |
| `cdp_create_campaign_template` | Create a new campaign template. Pass template type and entityId along with tenant list as JSON body. |
| `cdp_create_data_export` | Create a new data export definition. Body must be a JSON STRING containing at least `name` and `exportDefItems`. Pass folder_id to place the export in a specific folder (matches Vega UI which always sends ?folderId=).... |
| `cdp_create_dispatch` | Create a dispatch definition for a campaign. Pass dispatch definition as a JSON string. |
| `cdp_create_message_def` | Create standalone message definitions. Pass as a JSON string list. WARNING: standalone messageDefs created here CANNOT be referenced from a campaign by resourceId — the server rejects shared references with E0420. For... |
| `cdp_delete_audience_def` | Delete an audience definition |
| `cdp_delete_campaign` | Delete a campaign definition by ID |
| `cdp_delete_data_export` | Delete a data export definition by ID. |
| `cdp_delete_dispatch` | Delete a dispatch definition |
| `cdp_delete_message_def` | Delete a message definition by ID |
| `cdp_execute_audience_def` | Execute/calculate an audience definition. Triggers the audience calculation workflow. |
| `cdp_get_audience_def` | Get a specific audience definition by ID |
| `cdp_get_campaign` | Get a specific campaign definition by ID |
| `cdp_get_campaign_run` | Get details of a specific campaign execution (dataset description) by ID |
| `cdp_get_data_export` | Get a specific data export definition by ID. |
| `cdp_get_dataset_def` | Get a specific datasetDef by ID. |
| `cdp_get_dispatch` | Get a specific dispatch definition by ID |
| `cdp_get_message_def` | Get a specific message definition by ID |
| `cdp_get_run_dispatches` | Get the latest execution status for a campaign definition. Requires defId and defType. Optionally include step details. |
| `cdp_list_audience_defs` | List audience definitions for a tenant. Returns paged results. |
| `cdp_list_campaign_runs` | List execution history (dataset descriptions) for a campaign definition. Requires defId and defType (e.g. DATASET_DEF). Returns paged results. |
| `cdp_list_campaign_templates` | List available campaign templates. Requires type parameter (e.g. PLAYBOOK, MESSAGE, AUDIENCE). |
| `cdp_list_campaigns` | List all campaign definitions for a tenant. Returns paged results. |
| `cdp_list_data_exports` | List all data export definitions for a tenant. |
| `cdp_list_dataset_defs` | List datasetDefs (raw audience definitions) for a tenant. Useful for discovering shared definitions before calling cdp_copy_datasetdef. |
| `cdp_list_dispatches` | List dispatch definitions for a campaign |
| `cdp_list_message_defs` | List message definitions for a tenant. Returns paged results. |
| `cdp_lookup_audience_defs` | Lookup audiences by name. Returns matching audience definitions with optional offset/limit. |
| `cdp_publish_web_campaign` | Publish a triggered/web campaign via the CAMPAIGN_FLOW_DEFAULT workflow. This is the correct action for real-time/triggered campaigns (web, API, journey) — cdp_start_campaign only works for batch 'send now' runs. Mirr... |
| `cdp_run_data_export` | Execute a data export immediately via the DATA_EXPORT_DEFAULT workflow. Equivalent to clicking 'Send Now' in the Vega Data Export UI. Sends body `{"dataExportProperties":"{}"}` to match the UI contract. |
| `cdp_start_campaign` | Execute/run a campaign immediately ('send now'). Requires entity_id (the campaign def resourceId). Set cohort=True for cohort campaigns. An empty `{"campaignProperties":"{}"}` body is sent automatically to match the V... |
| `cdp_stop_campaign` | Stop/kill a running campaign by ID. Sends a workflow kill signal. |
| `cdp_update_audience_def` | Update an existing audience definition. Pass updated fields as a JSON string. |
| `cdp_update_campaign` | Update an existing campaign definition. Pass updated fields as a JSON string. Pass folder_id to move the campaign into a specific folder (matches UI save behaviour, which always sends ?folderId=...). |
| `cdp_update_data_export` | Update an existing data export definition. Pass updated fields as a JSON string. folder_id moves the export between folders. |
| `cdp_update_dispatch` | Update a dispatch definition. Pass updated fields as a JSON string. |
| `cdp_update_message_def` | Update a message definition by ID. Pass updated fields as a JSON string. |

## Config API — tenants, workflows, schedules, UDMP, DQE, clusters, connectors, mappings

<a id="config-api"></a>

| Tool | Description |
|------|-------------|
| `cdp_activate_schedule` | Activate a schedule. This triggers the schedule's workflow action via the workflow controller. |
| `cdp_create_a360_rule` | Create a new A360 identity resolution rule. Pass rule as a JSON string. |
| `cdp_create_column_validator` | Create a new column validator. Pass validator as a JSON string. |
| `cdp_create_compaction_request` | Create a new compaction request. Pass request details as a JSON string. |
| `cdp_create_execution_bucket` | Create a new execution bucket. Pass configuration as a JSON string. |
| `cdp_create_execution_summary_group` | Create a new execution summary group. Pass configuration as a JSON string. |
| `cdp_create_mapping_template` | Create a new mapping template. Pass template as a JSON string. |
| `cdp_create_output_connector` | Create a new output connector. Pass configuration as a JSON string. |
| `cdp_create_output_connector_def` | Create a new output connector definition. Pass definition as a JSON string. |
| `cdp_create_schedule` | Create a new schedule row in config/schedules. `body` is a JSON string of the schedule body. Canonical shape (from ui-core ScheduleService.save): |
| `cdp_deactivate_schedule` | Deactivate a schedule. This triggers the schedule's workflow action via the workflow controller. |
| `cdp_delete_a360_rule` | Delete an A360 rule |
| `cdp_delete_column_validator` | Delete a column validator |
| `cdp_delete_execution_bucket` | Delete an execution bucket |
| `cdp_delete_execution_summary_group` | Delete an execution summary group |
| `cdp_delete_mapping_template` | Delete a mapping template |
| `cdp_delete_output_connector` | Delete an output connector |
| `cdp_delete_output_connector_def` | Delete an output connector definition |
| `cdp_delete_schedule` | Delete a schedule (DELETE config/schedules/{id}). IMPORTANT: the UI fires cdp_invoke_workflow_action(action='unschedule', scheduleId=...) FIRST to detach the schedule from its runner workflow; doing only the DELETE le... |
| `cdp_deploy_workflow` | Deploy a workflow (make it active) |
| `cdp_generate_query` | Generate a SQL query from a dataset definition. Pass the dataset definition as a JSON string. |
| `cdp_get_a360_rule` | Get a specific A360 rule by ID |
| `cdp_get_column_validator` | Get a specific column validator by ID |
| `cdp_get_dqe1_rule` | Get a specific DQE Phase 1 rule by ID |
| `cdp_get_dqe2_rule` | Get a specific DQE Phase 2 rule by ID |
| `cdp_get_execution_summary_group` | Get a specific execution summary group by ID |
| `cdp_get_mapping_template` | Get a specific mapping template by ID |
| `cdp_get_output_connector` | Get a specific output connector by ID |
| `cdp_get_output_connector_def` | Get a specific output connector definition by ID |
| `cdp_get_schedule` | Get a specific schedule by ID |
| `cdp_get_schema_checkpoints` | Get schema checkpoints for a tenant |
| `cdp_get_summary_customization` | Get a specific summary customization by ID |
| `cdp_get_tenant` | Get details of a specific tenant by ID. Tenant IDs are strings — may be numeric, a GUID, or a slug. |
| `cdp_get_udmp_table` | Get a specific UDMP table by ID |
| `cdp_get_workflow` | Get a specific workflow by ID. Optionally specify a version. |
| `cdp_get_workflow_job` | Get details of a specific workflow job execution. Requires the workflow_id and job_id. |
| `cdp_get_workflow_step` | Get a specific step in a workflow |
| `cdp_invoke_workflow_action` | Invoke an arbitrary action on a workflow. This is the generic escape hatch for action verbs that cdp_run_workflow does not support (it only sends action=run). Common verbs observed in the Vega/Config UI: |
| `cdp_kill_job` | Kill a running workflow job |
| `cdp_list_a360_rules` | List A360 identity resolution rules |
| `cdp_list_clusters` | List available compute clusters |
| `cdp_list_column_validators` | List column validators for a tenant |
| `cdp_list_compaction_requests` | List compaction requests for a tenant |
| `cdp_list_dqe1_rules` | List DQE Phase 1 data quality rules |
| `cdp_list_dqe2_rules` | List DQE Phase 2 data quality rules |
| `cdp_list_execution_buckets` | List execution buckets for a tenant |
| `cdp_list_execution_summary_groups` | List execution summary groups for a tenant |
| `cdp_list_mapping_templates` | List mapping templates for a tenant |
| `cdp_list_output_connector_defs` | List available output connector definitions |
| `cdp_list_output_connectors` | List all configured output connectors for a tenant |
| `cdp_list_provisioning_packages` | List available provisioning packages for a tenant |
| `cdp_list_schedules` | List schedules for a tenant. Requires a schedule type (e.g. 'workflow'). Optionally filter by entityType and entityId. |
| `cdp_list_summary_customizations` | List summary customizations for a tenant |
| `cdp_list_tenant_clusters` | List clusters assigned to the current tenant |
| `cdp_list_tenants` | List all tenants accessible to the current user |
| `cdp_list_udmp_resources` | List UDMP resources (available data resources in the platform) |
| `cdp_list_udmp_tables` | List UDMP (Unified Data Model Platform) tables |
| `cdp_list_workflow_edges` | List all edges (connections) in a workflow DAG |
| `cdp_list_workflow_step_types` | List available workflow step types (node types for workflow DAGs) |
| `cdp_list_workflow_steps` | List all steps (nodes) in a workflow DAG |
| `cdp_list_workflows` | List workflows for a tenant |
| `cdp_rerun_job` | Re-run a completed or failed workflow job |
| `cdp_resume_job` | Resume a suspended workflow job |
| `cdp_run_workflow` | Trigger a workflow execution. Optionally provide entityType/entityId for scoped runs, or scheduleId for scheduled runs. `body` is an optional JSON string — many workflows require a properties map, e.g. CAMPAIGN_FLOW_D... |
| `cdp_send_email` | Send an email of a specific type. email_type examples: support, alert, notification. Pass email details as a JSON string. |
| `cdp_suspend_job` | Suspend a running workflow job |
| `cdp_unschedule_compaction_request` | Unschedule a compaction request by ID |
| `cdp_update_a360_rule` | Update an existing A360 rule. Pass updated fields as a JSON string. |
| `cdp_update_column_validator` | Update a column validator. Pass updated fields as a JSON string. |
| `cdp_update_execution_bucket` | Update an execution bucket. Pass updated fields as a JSON string. |
| `cdp_update_execution_summary_group` | Update an execution summary group. Pass updated fields as a JSON string. |
| `cdp_update_mapping_template` | Update an existing mapping template. Pass updated fields as a JSON string. |
| `cdp_update_output_connector` | Update an existing output connector. Pass updated fields as a JSON string. |
| `cdp_update_output_connector_def` | Update an output connector definition. Pass updated fields as a JSON string. |
| `cdp_update_schedule` | Update an existing schedule row (PUT config/schedules/{id}). `body` is a JSON string of the full schedule body — see cdp_create_schedule for the canonical shape. Pass the same `referenceId`, `entityType`, `entityId` a... |

## Connectors — input/output connectors and connector templates

<a id="connectors"></a>

| Tool | Description |
|------|-------------|
| `cdp_create_connector` | Create a new connector. Provide name and connector_type for simple creation, or pass a full JSON body string for advanced configuration. Channel options: email, export, sms, ads, facebook, any. |
| `cdp_create_connector_template` | Create a new connector definition. Pass definition as a JSON string. |
| `cdp_delete_connector` | Delete a connector |
| `cdp_delete_connector_template` | Delete a connector definition |
| `cdp_get_connector` | Get a specific connector by ID |
| `cdp_get_connector_template` | Get a specific connector definition by ID |
| `cdp_get_connector_versions` | Get connector history / past batch runs for a connector |
| `cdp_list_connector_templates` | List available connector definitions (templates) |
| `cdp_list_connectors` | List all configured connectors for a tenant |
| `cdp_update_connector` | Update an existing connector. Pass updated fields as a JSON string. |

## Reports & Query — dashboards, widgets, cubes, sQueryDefs, report defs

<a id="reports"></a>

| Tool | Description |
|------|-------------|
| `cdp_copy_cubic_set_def` | Copy a CubicSetDef by ID. Creates a duplicate of the OLAP query definition. |
| `cdp_copy_dashboard` | Copy a dashboard by ID. Creates a duplicate of the dashboard. |
| `cdp_copy_report_def` | Copy a report definition by ID. Creates a duplicate of the report. |
| `cdp_copy_squery_def` | Copy a SQueryDef by ID. Creates a duplicate of the query definition. |
| `cdp_copy_widget` | Copy a widget by ID. Creates a duplicate of the widget. |
| `cdp_create_cubic_set_def` | Create a new CubicSetDef. Pass definition as a JSON string. Requires name. The model field should be a serialized Saiku JSON string. |
| `cdp_create_dashboard` | Create a new dashboard. Pass dashboard definition as a JSON string. Should include name and optionally description, widgets array, and layout. |
| `cdp_create_report_def` | Create a new report definition. Pass definition as a JSON string. Requires name and reportType ('CUBE' or 'RELATIONAL'). CUBE type uses cubicSetDef, RELATIONAL uses datasetOperation. |
| `cdp_create_squery_def` | Create a new SQueryDef. Pass definition as a JSON string. Requires name and expression (SQL query). |
| `cdp_create_widget` | Create a new widget. Pass widget definition as a JSON string. Requires name and visualizationType at minimum. |
| `cdp_delete_cubic_set_def` | Delete a CubicSetDef by ID |
| `cdp_delete_dashboard` | Delete a dashboard by ID |
| `cdp_delete_report_def` | Delete a report definition by ID |
| `cdp_delete_squery_def` | Delete a SQueryDef by ID. |
| `cdp_delete_widget` | Delete a widget by ID |
| `cdp_export_report_excel` | Export a report as an Excel pivot file. Requires cubeId and password. The export is generated from the cube data on the collection endpoint. |
| `cdp_generate_squery_def` | Generate input/output arguments for a SQueryDef from its expression. Pass a SQueryDef JSON with an expression field. Returns the def with arguments and outputAttributes filled in. |
| `cdp_get_cube_status` | Get the processing status of all OLAP cubes for a tenant. Returns the status of each cube including whether it is ready. |
| `cdp_get_cube_status_by_names` | Get the processing status of specific OLAP cubes by name. Pass a JSON array of cube unique names as a string. |
| `cdp_get_cubic_set_def` | Get a CubicSetDef by ID. Returns the full definition including the model (Saiku query JSON). |
| `cdp_get_dashboard` | Get a dashboard by ID. Returns full definition including widgets and layout structure. |
| `cdp_get_dimension_values` | Get the values for a specific dimension level within an OLAP cube hierarchy. Requires cube_id, dimension_id, hierarchy_id, and level_name. Use cdp_get_cube_metadata first to discover these identifiers. |
| `cdp_get_report_def` | Get a report definition by ID. Returns full definition including reportType, datasetOperation or cubicSetDef. |
| `cdp_get_squery_def` | Get a SQueryDef by ID. Returns the full definition including expression and arguments. |
| `cdp_get_widget` | Get a widget by ID. Returns full definition including reportDef and visualization settings. |
| `cdp_list_cube_metadata` | List all available OLAP cubes for a tenant. Returns cube unique names and captions. |
| `cdp_list_cubic_set_defs` | List all CubicSetDefs (OLAP query definitions) for a tenant. These define Saiku-based cube queries used by CUBE-type reports. |
| `cdp_list_dashboards` | List all accessible dashboards for a tenant |
| `cdp_list_report_defs` | List all report definitions for a tenant |
| `cdp_list_squery_defs` | List all SQueryDefs (SQL query definitions) for a tenant. |
| `cdp_list_widgets` | List all accessible widgets for a tenant. Returns id, name, editedby, editeddate by default. |
| `cdp_update_cubic_set_def` | Update an existing CubicSetDef by ID. Pass updated fields as a JSON string. |
| `cdp_update_dashboard` | Update an existing dashboard by ID. Pass updated fields as a JSON string. |
| `cdp_update_report_def` | Update an existing report definition by ID. Pass updated fields as a JSON string. |
| `cdp_update_squery_def` | Update an existing SQueryDef by ID. Pass updated fields as a JSON string. |
| `cdp_update_widget` | Update an existing widget by ID. Pass updated fields as a JSON string. |
| `cdp_validate_squery_def` | Validate a SQueryDef's expression, arguments, and output attributes. Checks that parameter names, data types, and counts match the expression. |

## Predictions & Content — prediction defs, templates, containers

<a id="predictions"></a>

| Tool | Description |
|------|-------------|
| `cdp_clone_prediction` | Clone a prediction definition — creates a copy with a new ID (POST /v2/{tenantId}/campaign/predictionDefs/{id}?action=copy). |
| `cdp_create_prediction` | Create a new prediction definition (POST /v2/{tenantId}/campaign/predictionDefs). Pass the full definition as a JSON string. |
| `cdp_delete_prediction` | Delete a prediction definition (DELETE /v2/{tenantId}/campaign/predictionDefs/{id}). |
| `cdp_get_prediction` | Get a specific prediction definition by ID (GET /v2/{tenantId}/campaign/predictionDefs/{id}). |
| `cdp_get_prediction_container` | Get a prediction result by container code. Optionally pass pid (person ID) and other query params. |
| `cdp_get_web_templates` | Get web personalization templates for a tenant |
| `cdp_list_predictions` | List prediction definitions for a tenant (GET /v2/{tenantId}/campaign/predictionDefs). Pass `q` (e.g. 'isPublished:true') for server-side filtering. |
| `cdp_update_prediction` | Update an existing prediction definition (PUT /v2/{tenantId}/campaign/predictionDefs/{id}). Pass updated fields as a JSON string. |

## Mailer — accounts, subusers, identifiers, batches

<a id="mailer"></a>

| Tool | Description |
|------|-------------|
| `cdp_get_mailer_identifier_by_campaign_dispatch` | Look up a mailer identifier by campaign + dispatch (GET /v2/{tenantId}/mailer/identifiers/campaign/{campaignId}/dispatch/{dispatchId}). |
| `cdp_process_mailer_batch` | Trigger processing of a mailer batch by id (POST /v2/{tenantId}/mailer/batches/{id}). Optional JSON body is forwarded as-is. |

## Emailable Pages

<a id="emailable-pages"></a>

| Tool | Description |
|------|-------------|
| `cdp_create_emailable_page` | Create an emailable page (POST /v2/{tenantId}/emailablepages). Pass the page definition as a JSON string. |
| `cdp_delete_emailable_page` | Soft-delete an emailable page (DELETE /v2/{tenantId}/emailablepages/{id}). |
| `cdp_get_emailable_page` | Get an emailable page by id (GET /v2/{tenantId}/emailablepages/{id}). |
| `cdp_list_emailable_pages` | List emailable pages (GET /v2/{tenantId}/emailablepages). |
| `cdp_restore_emailable_page` | Restore a soft-deleted emailable page (POST /v2/{tenantId}/emailablepages/{id}). |
| `cdp_update_emailable_page` | Update an emailable page (PUT /v2/{tenantId}/emailablepages/{id}). Pass the updated definition as a JSON string. |

## Security — token, authentication, SSO, password reset

<a id="security"></a>

| Tool | Description |
|------|-------------|
| `cdp_check_sso_state` | Check the SSO state for a given user. Returns whether SSO is required for the user, optionally scoped to a specific tenant. |
| `cdp_create_token` | Create an access token using Basic authentication. Credentials are sent via the standard Authorization header. Returns access_token, token_type, expires_in. |
| `cdp_extend_token` | Extend the expiry of an existing bearer token. The token is sent via the Authorization header. |
| `cdp_generate_password_reset` | Generate a password reset link for a user. Sends a reset email to the user's registered address. Requires the username and source (VEGA or CONFIG). |
| `cdp_get_session_info` | Get session and permissions info for the current bearer token. Optionally specify a tenant_name to scope the response. |
| `cdp_get_token` | Get token information. Pass a bearer token to fetch info about that specific token, or username/password (Basic auth) to fetch the user's token. |
| `cdp_login` | Authenticate a user via Basic auth and generate a bearer token. Optionally specify a tenant_name to scope the login. Returns access_token, token_type, expires_in. |
| `cdp_logout` | Logout and revoke the current bearer token. Pass a bearer token to revoke it, or username/password to revoke all tokens for that user. |
| `cdp_revoke_token` | Revoke an access token. Pass either a bearer token to revoke that specific token, or username/password (Basic auth) to revoke all tokens for that user. |
| `cdp_update_password` | Update a user's password using a valid reset code. Requires the username, reset code, and new password. |
| `cdp_validate_password_reset` | Validate a password reset code. Checks whether the reset code is still valid for the given user. |

## Cache operations

<a id="cache"></a>

| Tool | Description |
|------|-------------|
| `cdp_cache_delete_by_group` | Delete a cache entry by group and ID. Returns 204 on success. |
| `cdp_cache_delete_by_id` | Delete a cache entry by ID. Returns 204 on success. |
| `cdp_cache_delete_by_key` | Delete a cache entry by explicit key. Returns 204 on success. |
| `cdp_cache_get_by_group` | Get a cached value by group and ID. Groups logically segregate cache keys by source or purpose. |
| `cdp_cache_get_by_id` | Get a cached value by ID. The cache key is auto-generated using the ID and any query parameters. |
| `cdp_cache_get_by_key` | Get a cached value by explicit cache key. Returns the stored value string and metadata. |
| `cdp_cache_put_by_group` | Set or update a cache entry by group and ID. |
| `cdp_cache_put_by_id` | Set or update a cache entry by ID. The cache key is auto-generated. |
| `cdp_cache_put_by_key` | Set or update a cache entry by explicit key. Value is stored as a string. Optional expiryTime in seconds. |

## Spam score

<a id="spam"></a>

| Tool | Description |
|------|-------------|
| `cdp_score_spam` | Score email/message content for spam likelihood (POST /v2/{tenantId}/spam/score). The request body MUST be a JSON ARRAY: [{"subject": "...", "body": "...", "fromAddress": "...", "fromName": "..."}]. Passing a single o... |

## Status — job status, orchestration, purge

<a id="status"></a>

| Tool | Description |
|------|-------------|
| `cdp_get_orchestration_status` | Get a single orchestration status record by id (GET /v2/{tenantId}/orchstatus/{id}). |
| `cdp_get_orchestration_status_for_connector` | Get orchestration status for a specific connector (GET /v2/{tenantId}/orchstatus/connector/{connectorId}). |
| `cdp_get_orchestration_status_log` | Fetch the log for an orchestration status record (GET /v2/{tenantId}/orchstatus/{id}/log). |
| `cdp_get_purge_status` | Get data-purge status (GET /v2/{tenantId}/purgestatus). If event_id is supplied, returns status for that specific purge event. |
| `cdp_get_status_message` | Get status messages for a workflow/entity event (GET /v2/{tenantId}/status/{resourceType}). resource_type defaults to 'statusmessage' (the only documented resource today) but the controller is generic — pass a differe... |
| `cdp_list_orchestration_status` | List orchestration statuses (GET /v2/{tenantId}/orchstatus). Returns workflow/connector orchestration runs and their state. |

## Self-Service Provisioning

<a id="provisions"></a>

| Tool | Description |
|------|-------------|
| `cdp_create_provision_instance` | Provision a new instance (POST /provisions/instances). Pass request body as JSON string with serviceId, provisionName, etc. |
| `cdp_deactivate_provision_instance` | Deactivate a provisioned instance (DELETE /provisions/instances/{id}). |
| `cdp_deprovision_instance` | Deprovision a provisioned instance (DELETE /provisions/instances/deprovision/{id}). |
| `cdp_get_mapped_provision_instance` | Get a mapped provisioned resource by instance ID (GET /provisions/instances/mapped/{instanceId}). |
| `cdp_get_provision_instance` | Get a specific provisioned instance by ID. |
| `cdp_get_provision_limit` | Get provisioning limit for a specific service (GET /provisions/limits/{serviceId}). Set validate=true to include a 'provisioningAllowed' flag. |
| `cdp_get_provision_service` | Get a specific provision service by ID or name (GET /provisions/services/{serviceId\|serviceName}). |
| `cdp_list_connector_links` | Fetch all connector links (GET /provisions/links). |
| `cdp_list_connector_links_by_class` | Fetch connector links filtered by connector class (GET /provisions/links/connector-class?connectorClass=...). |
| `cdp_list_provision_instances` | List provisioned instances with optional filters: active, status, provision_name, requested_by. |
| `cdp_list_provision_limits` | Fetch provisioning limits for all services of a tenant. |
| `cdp_list_provision_services` | List available provision services for a tenant (paged). |
| `cdp_list_unlinked_provision_instances` | List unlinked provisioned instances for a connector class and type (GET /provisions/instances/unlinked?connectorClassName=&connectorType=). |
| `cdp_provision_instance_action` | Perform an action on a provision instance (POST /provisions/instances/{id}?action=...). Actions: regenerate_credentials, apply_policy_change. Pass optional body as JSON string (required for apply_policy_change). |
| `cdp_reactivate_provision_instance` | Reactivate a deactivated instance (POST /provisions/instances/reactivate/{id}). |
| `cdp_retry_provision_instance` | Retry provisioning a failed instance (POST /provisions/instances/retry-provision/{id}). Pass same body as initial provisioning as JSON string. |
| `cdp_update_provision_instance` | Modify a provisioned instance (PUT /provisions/instances/{id}). Pass update body as JSON string. |

## Global platform actions

<a id="global-actions"></a>

| Tool | Description |
|------|-------------|
| `cdp_clone_resource` | Clone any CDP resource instance. Creates a copy with a new ID and returns the cloned object. Works on any resource that supports versioning (campaigns, workflows, connectors, predictions, reports, etc.). The resource_... |
| `cdp_describe_resource` | Get the JSON Schema description of any CDP resource. Works on collections (e.g., 'report/widgets') or instances (e.g., 'report/widgets/123'). Returns field names, types, editability, and default page size for collecti... |
| `cdp_set_current_version` | Roll back any CDP resource to a specific version. Equivalent to GET version N then PUT as current. Returns the new version number. Works on any versioned resource. The resource_path must include the ID, e.g. 'workflow... |

## Query

<a id="query"></a>

| Tool | Description |
|------|-------------|
| `cdp_query_sql` | Execute a read-only SQL query against the CDP data warehouse (Impala SQL) using GET with query in URL. Suitable for short queries. For long queries, use cdp_query_sql_post instead. Only SELECT statements are supported. |
| `cdp_query_sql_post` | Execute a read-only SQL query via POST body. Use this for long queries that may exceed URL length limits. Only SELECT statements are supported. |

---

This file is generated from the live server. To regenerate after adding or renaming tools, list all tools via the MCP `list_tools` call and rebuild the tables — or drop a small script into the repo root and re-run it.
