"""
MCP Resource providers for CDP metadata.

Implements 8 MCP resource providers that expose CDP metadata as read-only
context for AI agents. Resources are different from tools — they provide
read-only data that agents can request for context without modifying state.

Resource URIs follow the pattern: cdp://tenant/{tenant_id}/{resourceType}

Each resource provider makes an API call to fetch the data when requested.
"""

from __future__ import annotations

import json
from importlib import resources as importlib_resources

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.http_client import http_client


def _read_doc(filename: str) -> str:
    """Read a markdown file from the cdp_mcp.docs package."""
    return importlib_resources.files("cdp_mcp.docs").joinpath(filename).read_text(encoding="utf-8")


def register_resources(server: FastMCP) -> None:
    """Register all MCP resource providers on the server."""

    @server.resource(
        "cdp://tenant/{tenant_id}/resources",
        name="tenant-resources",
        description="Lists available DW resources (entity types) for a tenant",
        mime_type="application/json",
    )
    async def tenant_resources(tenant_id: str) -> str:
        """List available DW resources (entity types) for a tenant."""
        result = await http_client.get(
            "dw/resources",
            tenant_id=tenant_id,
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/roles",
        name="tenant-roles",
        description="Lists available roles for a tenant",
        mime_type="application/json",
    )
    async def tenant_roles(tenant_id: str) -> str:
        """List available roles for a tenant."""
        result = await http_client.get(
            "roles",
            tenant_id=tenant_id,
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/workflows",
        name="tenant-workflows",
        description="Lists workflows for a tenant",
        mime_type="application/json",
    )
    async def tenant_workflows(tenant_id: str) -> str:
        """List workflows for a tenant."""
        result = await http_client.get(
            "workflows",
            tenant_id=tenant_id,
            path_style="none",
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/clusters",
        name="tenant-clusters",
        description="Lists compute clusters for a tenant",
        mime_type="application/json",
    )
    async def tenant_clusters(tenant_id: str) -> str:
        """List compute clusters for a tenant."""
        result = await http_client.get(
            "clusters",
            tenant_id=tenant_id,
            path_style="none",
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/udmp-tables",
        name="tenant-udmp-tables",
        description="Lists UDMP tables and their column schemas for a tenant",
        mime_type="application/json",
    )
    async def tenant_udmp_tables(tenant_id: str) -> str:
        """List UDMP tables and their column schemas."""
        result = await http_client.get(
            "UDMPTables",
            tenant_id=tenant_id,
            path_style="none",
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/cube-metadata",
        name="tenant-cube-metadata",
        description="Lists OLAP cube metadata (dimensions and measures) for a tenant",
        mime_type="application/json",
    )
    async def tenant_cube_metadata(tenant_id: str) -> str:
        """List OLAP cube metadata (dimensions and measures)."""
        result = await http_client.get(
            "report/cubeMetadata",
            tenant_id=tenant_id,
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/connector-templates",
        name="tenant-connector-templates",
        description="Lists available connector templates for a tenant",
        mime_type="application/json",
    )
    async def tenant_connector_templates(tenant_id: str) -> str:
        """List available connector templates."""
        result = await http_client.get(
            "template/connectors",
            tenant_id=tenant_id,
            path_style="none",
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://tenant/{tenant_id}/campaigns",
        name="tenant-campaigns",
        description="Lists campaign definitions for a tenant",
        mime_type="application/json",
    )
    async def tenant_campaigns(tenant_id: str) -> str:
        """List campaign definitions."""
        result = await http_client.get(
            "campaigndefs",
            tenant_id=tenant_id,
            path_style="none",
        )
        if not result.success:
            return json.dumps({"error": str(result.error)})
        return json.dumps(result.data, indent=2)

    @server.resource(
        "cdp://docs/campaign-playbook",
        name="campaign-playbook",
        description=(
            "Authoritative playbook for creating campaigns, audiences, and message "
            "definitions on CDP. Consult before calling cdp_create_campaign, "
            "cdp_update_campaign, cdp_create_message_def, cdp_create_audience_def, "
            "cdp_get_audience_count, or cdp_score_spam. Covers the inline-ownership "
            "rule, operator enum, time-window math, EXCLUDE behavior pattern, and "
            "body-as-JSON-string convention."
        ),
        mime_type="text/markdown",
    )
    async def campaign_playbook() -> str:
        """Return the authoritative campaign playbook (markdown)."""
        return _read_doc("campaign_playbook.md")

    @server.resource(
        "cdp://docs/orchestration-playbook",
        name="orchestration-playbook",
        description=(
            "Multi-step orchestration recipes the MCP cannot infer on its own: "
            "generic schedule lifecycle (create row + arm runner workflow + poll), "
            "connector publish/schedule/unschedule, report & data-export "
            "send-now and scheduled runs, sQueryDef generate-then-validate, "
            "provisioning via PROVISIONER_TOOL_DEFAULT, compaction, and the "
            "universal drain-before-delete rule. Consult before any action that "
            "touches config/schedules, config/workflows/{name}?action=..., or "
            "runner workflows (AIF_RUNNER, REPORT_RUNNNER_DEFAULT, "
            "DATA_EXPORT_DEFAULT, CAMPAIGN_FLOW_DEFAULT, CONNECTOR_OPS_DEFAULT)."
        ),
        mime_type="text/markdown",
    )
    async def orchestration_playbook() -> str:
        """Return the orchestration playbook (markdown)."""
        return _read_doc("orchestration_playbook.md")

    @server.resource(
        "cdp://docs/customer360-playbook",
        name="customer360-playbook",
        description=(
            "Authoritative flow for customer-360 retrieval, rendering, search, "
            "and identity purge. Covers the three parallel fetches a profile "
            "page requires (dw/a360/customers + UDMPTables + tenant 360 layout "
            "properties), the layout deep-merge rules, realtime polling, "
            "targetentity-based pagination, `fq` advanced-search encoding, and "
            "GDPR purge polling. Consult before calling cdp_get_customer_360*, "
            "cdp_request_data_erasure, or cdp_list_a360_rules."
        ),
        mime_type="text/markdown",
    )
    async def customer360_playbook() -> str:
        """Return the customer-360 playbook (markdown)."""
        return _read_doc("customer360_playbook.md")

    @server.resource(
        "cdp://docs/admin-ops-playbook",
        name="admin-ops-playbook",
        description=(
            "Admin and data-governance orchestration: DQE rule batches with "
            "dry-run-via-compaction, A360 rule three-phase saves, compaction "
            "lifecycle, status-page job control (rerun/kill/suspend/resume), "
            "GDPR erasure polling and override, provisioner package runs, "
            "content-model bulk template provisioning, user/role onboarding, "
            "and the universal drain-before-delete rule. Consult before any "
            "destructive multi-entity action."
        ),
        mime_type="text/markdown",
    )
    async def admin_ops_playbook() -> str:
        """Return the admin/ops playbook (markdown)."""
        return _read_doc("admin_ops_playbook.md")

    @server.resource(
        "cdp://docs/reports-dashboards-playbook",
        name="reports-dashboards-playbook",
        description=(
            "Authoritative flow for report definitions, cube (OLAP) reports, "
            "SQL-query reports, and dashboards. Covers the array-wrap POST "
            "contract ([reportDef] / [dashboard]), the REPORT_RUNNNER_DEFAULT "
            "(triple-N) send-now workflow, the ?folderId= requirement, cube "
            "metadata walk (cubemetadata → dimensions → hierarchies → levels), "
            "ad-hoc vs cached execution (?action=execute vs ?action=fetch), "
            "the BI_MAPPER_DEFAULT + A1_ORCHESTRATOR dual freshness check, "
            "dashboard uiProperties JSON-string layout serialization, and "
            "sQueryDef argument validation. Consult before calling "
            "cdp_create_report_def, cdp_create_dashboard, cdp_execute_report, "
            "cdp_fetch_report_data, or cdp_get_cube_status."
        ),
        mime_type="text/markdown",
    )
    async def reports_dashboards_playbook() -> str:
        """Return the reports & dashboards playbook (markdown)."""
        return _read_doc("reports_dashboards_playbook.md")

    @server.resource(
        "cdp://docs/workflow-authoring-playbook",
        name="workflow-authoring-playbook",
        description=(
            "Authoritative flow for authoring, modifying, deploying, and "
            "invoking configAPI workflows. Covers the symbolic workflowId vs "
            "numeric workflowDBId trap (URL segment vs entityId query param), "
            "the three parallel GETs required to materialize a workflow graph "
            "(workflows/{id} + /workflowSteps + /workflowEdges), versioning "
            "rules (query-string-only on deploy/delete), batch step POST/PUT "
            "vs per-script POST/PUT/DELETE for mapping scripts, full create→"
            "deploy sequence, invocation verb taxonomy (run/deploy/schedule/"
            "unschedule/activate_schedule/rerun/kill/publish), and the "
            "drain-before-delete rule. Consult before any cdp_create_workflow, "
            "cdp_update_workflow, cdp_delete_workflow, cdp_run_workflow, or "
            "cdp_invoke_workflow_action call."
        ),
        mime_type="text/markdown",
    )
    async def workflow_authoring_playbook() -> str:
        """Return the workflow authoring playbook (markdown)."""
        return _read_doc("workflow_authoring_playbook.md")

    @server.resource(
        "cdp://docs/connector-wizard-playbook",
        name="connector-wizard-playbook",
        description=(
            "Authoritative flow for connector CRUD, publish, schedule, and "
            "unschedule. Covers input vs output endpoint swap (connectors vs "
            "outputConnectors), the 4-or-5-step wizard with ssidPrefix-based "
            "branching (inputConnectorsToSkip / intervalConnectors), the "
            "create → CONNECTOR_OPS_DEFAULT?action=publish two-step, the "
            "3-step schedule orchestration (GET AIF_RUNNER id → POST schedules → "
            "POST AIF_RUNNER?action=schedule) with the referenceId vs entityId "
            "trap, the reverse 2-step unschedule-then-delete, the [entity, "
            "[columns]] mapping tuple shape, parameter completion and "
            "dateStarted requirements. Consult before any cdp_create_connector, "
            "cdp_publish_connector, or connector-schedule call."
        ),
        mime_type="text/markdown",
    )
    async def connector_wizard_playbook() -> str:
        """Return the connector wizard playbook (markdown)."""
        return _read_doc("connector_wizard_playbook.md")

    @server.resource(
        "cdp://docs/udmp-metadata-playbook",
        name="udmp-metadata-playbook",
        description=(
            "Authoritative flow for UDMP tables/columns, column validators, "
            "mapping templates, content-model templates, and tenant "
            "properties. Covers the nested {columns: {content: []}} read "
            "shape vs flat {columns: []} write shape, parallel POST/PUT/DELETE "
            "batch saveResources (non-transactional), the UDMPTables → "
            "UDMPResources cascade, schema publish ordering (pause consumers "
            "first), custom-attribute whitelist gating via "
            "summaryEntity.customAttribute.whitelist, idempotent PUT for "
            "tableoverrides, the unusual PUT templates/provision?action=update "
            "contract for content models, and the customer360 / "
            "default.360.layout vs tenant.360.layout protection rule. Consult "
            "before modifying UDMP tables, column validators, templates, or "
            "tenant properties."
        ),
        mime_type="text/markdown",
    )
    async def udmp_metadata_playbook() -> str:
        """Return the UDMP/metadata playbook (markdown)."""
        return _read_doc("udmp_metadata_playbook.md")

