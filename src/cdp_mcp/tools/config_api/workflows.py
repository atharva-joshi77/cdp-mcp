"""
Workflow tools for CDP Config API.

Implements MCP tools for workflow CRUD, steps, edges, and actions.
Source: acquia/cdp-configapi WorkflowController.java
Endpoints: /v2/{tenantId}/config/workflows
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_workflow_tools(server: FastMCP) -> None:
    """Register all workflow tools on the MCP server."""

    @server.tool(
        name="cdp_list_workflows",
        description="List workflows for a tenant",
    )
    async def cdp_list_workflows(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List workflows for a tenant."""
        result = await http_client.get(
            "config/workflows",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_workflow",
        description="Get a specific workflow by ID. Optionally specify a version.",
    )
    async def cdp_get_workflow(
        workflow_id: str,
        version: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific workflow by ID."""
        result = await http_client.get(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"version": version},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_run_workflow",
        description=(
            "Trigger a workflow execution. "
            "Optionally provide entityType/entityId for scoped runs, "
            "or scheduleId for scheduled runs. "
            "`body` is an optional JSON string — many workflows require a "
            "properties map, e.g. CAMPAIGN_FLOW_DEFAULT needs "
            '`{\"campaignProperties\":\"{}\"}`, DATA_EXPORT_DEFAULT needs '
            '`{\"dataExportProperties\":\"{}\"}`. When omitted, no body is sent.'
        ),
    )
    async def cdp_run_workflow(
        workflow_id: str,
        version: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        schedule_id: Optional[int] = None,
        body: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Trigger a workflow execution."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={
                "action": "run",
                "version": version,
                "entityType": entity_type,
                "entityId": entity_id,
                "scheduleId": schedule_id,
            },
            body=json.loads(body) if body else None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_deploy_workflow",
        description="Deploy a workflow (make it active)",
    )
    async def cdp_deploy_workflow(
        workflow_id: str,
        version: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Deploy a workflow (make it active)."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "deploy", "version": version},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_list_workflow_steps",
        description="List all steps (nodes) in a workflow DAG",
    )
    async def cdp_list_workflow_steps(
        workflow_id: str,
        version: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """List all steps (nodes) in a workflow DAG."""
        result = await http_client.get(
            f"config/workflows/{workflow_id}/workflowSteps",
            tenant_id=tenant_id,
            params={"version": version},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_workflow_step",
        description="Get a specific step in a workflow",
    )
    async def cdp_get_workflow_step(
        workflow_id: str,
        step_id: str,
        version: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific step in a workflow."""
        result = await http_client.get(
            f"config/workflows/{workflow_id}/workflowSteps/{step_id}",
            tenant_id=tenant_id,
            params={"version": version},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_list_workflow_edges",
        description="List all edges (connections) in a workflow DAG",
    )
    async def cdp_list_workflow_edges(
        workflow_id: str,
        version: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """List all edges (connections) in a workflow DAG."""
        result = await http_client.get(
            f"config/workflows/{workflow_id}/workflowEdges",
            tenant_id=tenant_id,
            params={"version": version},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_invoke_workflow_action",
        description=(
            "Invoke an arbitrary action on a workflow. This is the generic "
            "escape hatch for action verbs that cdp_run_workflow does not "
            "support (it only sends action=run). Common verbs observed in the "
            "Vega/Config UI:\n"
            "- 'schedule' / 'unschedule'  — arm/disarm a schedule on AIF_RUNNER, "
            "REPORT_RUNNNER_DEFAULT, DATA_EXPORT_DEFAULT, etc. Requires schedule_id.\n"
            "- 'activate_schedule' / 'deactivate_schedule' — toggle an existing "
            "schedule without deleting the row (also exposed via "
            "cdp_activate_schedule / cdp_deactivate_schedule).\n"
            "- 'publish' / 'unpublish' — connector lifecycle via "
            "CONNECTOR_OPS_DEFAULT. Requires entity_type='connector' + entity_id.\n"
            "- 'run' — alias of cdp_run_workflow, kept for completeness.\n"
            "`body` is an optional JSON string for workflows that need a payload."
        ),
    )
    async def cdp_invoke_workflow_action(
        workflow_id: str,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        schedule_id: Optional[int] = None,
        version: Optional[int] = None,
        body: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Invoke an arbitrary action on a workflow."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={
                "action": action,
                "version": version,
                "entityType": entity_type,
                "entityId": entity_id,
                "scheduleId": schedule_id,
            },
            body=json.loads(body) if body else None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

