"""
Campaign metadata tools for CDP Data Warehouse API.

Implements 1 MCP tool: get campaign output attributes.
Source: acquia/cdp-dwapi DwCampaignMetaApiController.java
Endpoints: /v2/{tenantId}/dw/campaign/outputAttributes
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_campaign_meta_tools(server: FastMCP) -> None:
    """Register campaign metadata tools on the MCP server."""

    @server.tool(
        name="cdp_get_campaign_output_attributes",
        description=(
            "Get the output attribute columns for a campaign definition. "
            "Pass campaign definition as a JSON string."
        ),
    )
    async def cdp_get_campaign_output_attributes(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get the output attribute columns for a campaign definition."""
        result = await http_client.post(
            "dw/campaign/outputAttributes",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
