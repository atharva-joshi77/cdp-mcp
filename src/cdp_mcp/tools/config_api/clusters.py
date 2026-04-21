"""
Cluster and workflow step type tools for CDP Config API.

Implements 3 MCP tools: list clusters, list tenant clusters, list workflow step types.
Source: acquia/cdp-configapi ClusterController, TenantClusterController, WorkflowStepTypeController
Endpoints: /v2/{tenantId}/config/clusters, config/tenantClusters, config/workflowStepTypes
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_cluster_tools(server: FastMCP) -> None:
    """Register all cluster and workflow step type tools on the MCP server."""

    @server.tool(
        name="cdp_list_clusters",
        description="List available compute clusters",
    )
    async def cdp_list_clusters(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List available compute clusters."""
        result = await http_client.get(
            "config/clusters",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_list_tenant_clusters",
        description="List clusters assigned to the current tenant",
    )
    async def cdp_list_tenant_clusters(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List clusters assigned to the current tenant."""
        result = await http_client.get(
            "config/tenantClusters",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_list_workflow_step_types",
        description="List available workflow step types (node types for workflow DAGs)",
    )
    async def cdp_list_workflow_step_types(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List available workflow step types."""
        result = await http_client.get(
            "config/workflowStepTypes",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
