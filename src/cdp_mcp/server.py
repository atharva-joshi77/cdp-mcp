"""
MCP Server setup and tool registration hub.

Creates the FastMCP server instance. Tool registration functions
from each phase module will be imported and called here.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from cdp_mcp.tools.permissions.users import register_user_tools
from cdp_mcp.tools.permissions.roles import register_role_tools
from cdp_mcp.tools.permissions.clients import register_client_tools
from cdp_mcp.tools.permissions.users_lite import register_user_lite_tools
from cdp_mcp.tools.permissions.selfservice_roles import register_self_service_role_tools
from cdp_mcp.tools.permissions.selfservice_users import register_self_service_user_tools

from cdp_mcp.tools.dw.entities import register_entity_tools
from cdp_mcp.tools.dw.a360 import register_a360_tools
from cdp_mcp.tools.dw.audience import register_audience_tools
from cdp_mcp.tools.dw.tracker import register_tracker_tools
from cdp_mcp.tools.dw.data_erasure import register_data_erasure_tools
from cdp_mcp.tools.dw.offers import register_offer_tools
from cdp_mcp.tools.dw.metadata import register_metadata_tools
from cdp_mcp.tools.dw.reports import register_dw_report_tools
from cdp_mcp.tools.dw.purge import register_purge_tools
from cdp_mcp.tools.dw.campaign_meta import register_campaign_meta_tools
from cdp_mcp.tools.dw.rtmeta import register_rtmeta_tools

from cdp_mcp.tools.campaign.definitions import register_campaign_def_tools
from cdp_mcp.tools.campaign.actions import register_campaign_action_tools
from cdp_mcp.tools.campaign.dispatches import register_dispatch_tools
from cdp_mcp.tools.campaign.runs import register_campaign_run_tools
from cdp_mcp.tools.campaign.audiences import register_audience_def_tools
from cdp_mcp.tools.campaign.templates import register_campaign_template_tools
from cdp_mcp.tools.campaign.messages import register_message_def_tools
from cdp_mcp.tools.campaign.data_exports import register_data_export_tools
from cdp_mcp.tools.campaign.dataset_defs import register_dataset_def_tools

from cdp_mcp.tools.config_api.tenants import register_tenant_tools
from cdp_mcp.tools.config_api.workflows import register_workflow_tools
from cdp_mcp.tools.config_api.schedules import register_schedule_tools
from cdp_mcp.tools.config_api.workflow_jobs import register_workflow_job_tools
from cdp_mcp.tools.config_api.udmp import register_udmp_tools
from cdp_mcp.tools.config_api.dqe_rules import register_dqe_rule_tools
from cdp_mcp.tools.config_api.clusters import register_cluster_tools
from cdp_mcp.tools.config_api.summary_customizations import register_summary_customization_tools
from cdp_mcp.tools.config_api.output_connectors import register_output_connector_tools
from cdp_mcp.tools.config_api.output_connector_defs import register_output_connector_def_tools
from cdp_mcp.tools.config_api.a360_rules import register_a360_rule_tools
from cdp_mcp.tools.config_api.mapping_templates import register_mapping_template_tools
from cdp_mcp.tools.config_api.compaction_requests import register_compaction_request_tools
from cdp_mcp.tools.config_api.execution_buckets import register_execution_bucket_tools
from cdp_mcp.tools.config_api.execution_summary_groups import register_execution_summary_group_tools
from cdp_mcp.tools.config_api.column_validators import register_column_validator_tools
from cdp_mcp.tools.config_api.schema_checkpoints import register_schema_checkpoint_tools
from cdp_mcp.tools.config_api.emails import register_email_tools
from cdp_mcp.tools.config_api.provisioning import register_provisioning_tools
from cdp_mcp.tools.config_api.query_generator import register_query_generator_tools

from cdp_mcp.tools.connectors.connectors import register_connector_tools
from cdp_mcp.tools.connectors.templates import register_connector_template_tools
from cdp_mcp.tools.predictions.predictions import register_prediction_tools
from cdp_mcp.tools.predictions.content import register_content_tools
from cdp_mcp.tools.alerts.alerts import register_alert_tools

from cdp_mcp.tools.reports.widgets import register_widget_tools
from cdp_mcp.tools.reports.dashboards import register_dashboard_tools
from cdp_mcp.tools.reports.cubic_set_defs import register_cubic_set_def_tools
from cdp_mcp.tools.reports.report_defs import register_report_def_tools
from cdp_mcp.tools.reports.cube_metadata import register_cube_metadata_tools
from cdp_mcp.tools.reports.cube_status import register_cube_status_tools
from cdp_mcp.tools.reports.squery_defs import register_squery_def_tools
from cdp_mcp.tools.query.ql import register_query_language_tools

from cdp_mcp.tools.cache.cache_ops import register_cache_tools
from cdp_mcp.tools.security.auth import register_security_tools
from cdp_mcp.tools.security.password_reset import register_password_reset_tools
from cdp_mcp.tools.security.sso import register_sso_tools
from cdp_mcp.tools.global_actions.global_actions import register_global_action_tools
from cdp_mcp.tools.spam.spam import register_spam_tools
from cdp_mcp.tools.status.status import register_status_tools
from cdp_mcp.tools.provisions.provisions import register_provisions_tools
from cdp_mcp.tools.emailable_pages.emailable_pages import register_emailable_pages_tools
from cdp_mcp.tools.mailer.mailer import register_mailer_tools
from cdp_mcp.resources.resource_providers import register_resources


def create_server() -> FastMCP:
    """Create and configure the CDP MCP Server."""
    server = FastMCP(
        name="cdp-mcp-server",
        instructions=(
            "MCP Server for Acquia Customer Data Platform (CDP). Provides tools "
            "for managing users, roles, data warehouse entities, campaigns, "
            "workflows, connectors, predictions, alerts, reports, and more across "
            "CDP tenants.\n\n"
            "CRITICAL RULES — read before calling campaign/audience/message tools:\n"
            "- Campaigns OWN their audience and messages INLINE. Do NOT call "
            "cdp_create_audience_def (endpoint unsupported) or create standalone "
            "messageDefs that you then reference from a campaign — shared "
            "messageDefs are rejected with E0420. Instead: call cdp_create_campaign "
            "with just name+description, then cdp_update_campaign with the full "
            "body containing inline 'audience' and inline 'messageDefs' objects.\n"
            "- Tools with a `body` parameter expect a JSON STRING, not a dict. "
            "Build the object, then json.dumps() before passing.\n"
            "- DatasetDef comparison operators use the _EQUALS suffix, NOT _OR_EQUAL: "
            "LESS_THAN_EQUALS, GREATER_THAN_EQUALS, EQUALS, NOT_EQUALS. Other valid "
            "operators: AND, OR, NOT, IN, BETWEEN, LIKE, NOW, SUBTRACT, ADD, "
            "DISTINCT, PASSED_ARGUMENT. Using *_OR_EQUAL fails parse.\n"
            "- Time-window filters use millisecond math on timestamp attributes: "
            "NOW - N*86400000 (e.g. 30 days = 2592000000, 14 days = 1209600000).\n"
            "- 'Has NOT done X in last Y days' uses the customer-entity EXCLUDE "
            "pattern with two datasetDefInput branches; event string literals go "
            "in single quotes inside VALUE nodes (e.g. \"value\": \"'emailOpened'\").\n"
            "- cdp_score_spam body is a JSON ARRAY [{...}], not a single object.\n"
            "- Attribute names like 'recency', 'DaysSinceLastOrder' are NOT "
            "universally present. To discover available attributes without admin "
            "perms: call cdp_list_campaigns and scan for "
            "{\"inputType\":\"ATTRIBUTES\",\"attributes\":[...]} nodes.\n\n"
            "For full details, patterns, reference campaigns, and body templates, "
            "fetch the resource cdp://docs/campaign-playbook.\n"
            "For multi-step orchestration (schedules, connector publish, "
            "report/export send-now, provisioner, compaction, job control) "
            "fetch cdp://docs/orchestration-playbook.\n"
            "For customer-360 retrieval/search/identity purge (parallel UDMP + "
            "layout + a360/customers fetches, `fq` encoding) fetch "
            "cdp://docs/customer360-playbook.\n"
            "For admin/governance (DQE batches, A360 three-phase saves, GDPR "
            "erasure, provisioner, drain-before-delete) fetch "
            "cdp://docs/admin-ops-playbook.\n"
            "For reports, cube (OLAP) queries, SQL reports, and dashboards "
            "(array-wrap POSTs, REPORT_RUNNNER_DEFAULT triple-N workflow, "
            "cube metadata walk, BI freshness dual-check, uiProperties JSON "
            "serialization) fetch cdp://docs/reports-dashboards-playbook.\n"
            "For authoring configAPI workflows (3-parallel-GET graph load, "
            "workflowId vs workflowDBId trap, versioning in query-string only, "
            "batch step POST/PUT vs per-script mapping scripts, create→deploy "
            "sequence, invocation verb taxonomy) fetch "
            "cdp://docs/workflow-authoring-playbook.\n"
            "For connector CRUD, publish, schedule, and unschedule (input vs "
            "output endpoint swap, wizard step branching, 3-step AIF_RUNNER "
            "schedule orchestration, referenceId vs entityId trap, reverse "
            "unschedule-then-delete, mapping tuple shape) fetch "
            "cdp://docs/connector-wizard-playbook.\n"
            "For UDMP tables/columns, column validators, mapping templates, "
            "content-model templates, and tenant properties (nested columns "
            "read vs flat write, parallel saveResources batch, UDMPTables→"
            "UDMPResources cascade, custom-attribute whitelist gate, PUT "
            "templates/provision?action=update, 360 layout protection) fetch "
            "cdp://docs/udmp-metadata-playbook."
        ),
    )

    # Phase 2: Permissions API (15 tools)
    register_user_tools(server)
    register_role_tools(server)
    register_client_tools(server)
    register_user_lite_tools(server)
    register_self_service_role_tools(server)
    register_self_service_user_tools(server)

    # Phase 3: Data Warehouse API (21 tools)
    register_entity_tools(server)
    register_a360_tools(server)
    register_audience_tools(server)
    register_tracker_tools(server)
    register_data_erasure_tools(server)
    register_offer_tools(server)
    register_metadata_tools(server)
    register_dw_report_tools(server)
    register_purge_tools(server)
    register_campaign_meta_tools(server)
    register_rtmeta_tools(server)

    # Phase 4: Campaign API (24 tools)
    register_campaign_def_tools(server)
    register_campaign_action_tools(server)
    register_dispatch_tools(server)
    register_campaign_run_tools(server)
    register_audience_def_tools(server)
    register_campaign_template_tools(server)
    register_message_def_tools(server)
    register_data_export_tools(server)
    register_dataset_def_tools(server)

    # Phase 5: Config API (30 tools)
    register_tenant_tools(server)
    register_workflow_tools(server)
    register_schedule_tools(server)
    register_workflow_job_tools(server)
    register_udmp_tools(server)
    register_dqe_rule_tools(server)
    register_cluster_tools(server)
    register_summary_customization_tools(server)
    register_output_connector_tools(server)
    register_output_connector_def_tools(server)
    register_a360_rule_tools(server)
    register_mapping_template_tools(server)
    register_compaction_request_tools(server)
    register_execution_bucket_tools(server)
    register_execution_summary_group_tools(server)
    register_column_validator_tools(server)
    register_schema_checkpoint_tools(server)
    register_email_tools(server)
    register_provisioning_tools(server)
    register_query_generator_tools(server)

    # Phase 6: Connectors, Predictions, Alerts (27 tools)
    register_connector_tools(server)
    register_connector_template_tools(server)
    register_prediction_tools(server)
    register_content_tools(server)
    register_alert_tools(server)

    # Phase 7: Reports & Query Language
    register_widget_tools(server)
    register_dashboard_tools(server)
    register_cubic_set_def_tools(server)
    register_report_def_tools(server)
    register_cube_metadata_tools(server)
    register_cube_status_tools(server)
    register_squery_def_tools(server)
    register_query_language_tools(server)

    # Phase 8: Cache, Security, Global Actions (16 tools)
    register_cache_tools(server)
    register_security_tools(server)
    register_password_reset_tools(server)
    register_sso_tools(server)
    register_global_action_tools(server)
    register_spam_tools(server)
    register_status_tools(server)
    register_provisions_tools(server)

    # Phase 9: Additional CDP services
    register_emailable_pages_tools(server)
    register_mailer_tools(server)

    # Phase 8: MCP Resources (8 resource providers)
    register_resources(server)

    return server


# Module-level server instance
mcp = create_server()
