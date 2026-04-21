"""
Offer retrieval tools for CDP Data Warehouse API.

Implements 1 MCP tool: get offers.
Source: apiSpecification/specs/dwAPI.yaml
Endpoint uses pathStyle "v2": /v2/{tenantId}/dw/offers
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_offer_tools(server: FastMCP) -> None:
    """Register offer retrieval tools on the MCP server."""

    @server.tool(
        name="cdp_get_offers",
        description=(
            "Retrieve available offers for a customer or segment. "
            "Pass offer request as a JSON string."
        ),
    )
    async def cdp_get_offers(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Retrieve available offers for a customer or segment."""
        result = await http_client.post(
            "dw/offers",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
