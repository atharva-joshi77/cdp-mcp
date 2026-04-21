"""
Campaign execution history tools for CDP Campaign API.

Implements 3 MCP tools: list runs (dataset descriptions), get run, get run status.
Source: acquia/cdp-campaignapi DatasetDescriptionController.java
Controller path: /v2/{tenantId}/campaign/datasetDescriptions
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_campaign_run_tools(server: FastMCP) -> None:
    """Register all campaign run/execution history tools on the MCP server."""

    @server.tool(
        name="cdp_list_campaign_runs",
        description=(
            "List execution history (dataset descriptions) for a campaign definition. "
            "Requires defId and defType (e.g. DATASET_DEF). Returns paged results."
        ),
    )
    async def cdp_list_campaign_runs(
        def_id: int,
        def_type: str = "DATASET_DEF",
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List execution history for a campaign definition."""
        params: dict = {"defId": def_id, "defType": def_type}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        result = await http_client.get(
            "campaign/datasetDescriptions",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_campaign_run",
        description="Get details of a specific campaign execution (dataset description) by ID",
    )
    async def cdp_get_campaign_run(
        run_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get details of a specific campaign execution."""
        result = await http_client.get(
            f"campaign/datasetDescriptions/{run_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_run_dispatches",
        description=(
            "Get the latest execution status for a campaign definition. "
            "Requires defId and defType. Optionally include step details."
        ),
    )
    async def cdp_get_run_dispatches(
        def_id: int,
        def_type: str = "DATASET_DEF",
        steps: bool = False,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get latest execution status for a campaign definition."""
        params: dict = {
            "defId": def_id,
            "defType": def_type,
            "action": "status",
        }
        if steps:
            params["steps"] = "true"

        result = await http_client.get(
            "campaign/datasetDescriptions",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
