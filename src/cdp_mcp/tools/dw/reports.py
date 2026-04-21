"""
DW report access tools for CDP Data Warehouse API.

Implements 2 MCP tools: fetch report, execute report.
These access reports through the DW API path (separate from the full Report API in Phase 7).
Source: apiSpecification/specs/dwAPI.yaml
Endpoints use pathStyle "v2": /v2/{tenantId}/dw/report/reportDefs/...
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_dw_report_tools(server: FastMCP) -> None:
    """Register DW report access tools on the MCP server."""

    @server.tool(
        name="cdp_dw_fetch_report",
        description="Fetch cached report results via the DW API path",
    )
    async def cdp_dw_fetch_report(
        report_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Fetch cached report results via the DW API path."""
        result = await http_client.get(
            f"dw/report/reportDefs/{report_id}",
            tenant_id=tenant_id,
            params={"action": "fetch"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_dw_execute_report",
        description=(
            "Execute a report in real-time via the DW API path. "
            "Pass report definition as a JSON string."
        ),
    )
    async def cdp_dw_execute_report(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Execute a report in real-time via the DW API path."""
        result = await http_client.post(
            "dw/report/reportDefs",
            tenant_id=tenant_id,
            params={"action": "execute"},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
