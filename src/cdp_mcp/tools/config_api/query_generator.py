"""
Query generator tools for CDP Config API.

Implements 1 MCP tool: generate dataset definition query.
Source: acquia/cdp-configapi DatasetDefQueryGeneratorController.java
Endpoints: /v2/{tenantId}/config/queryGenerator
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_query_generator_tools(server: FastMCP) -> None:
    """Register query generator tools on the MCP server."""

    @server.tool(
        name="cdp_generate_query",
        description=(
            "Generate a SQL query from a dataset definition. "
            "Pass the dataset definition as a JSON string."
        ),
    )
    async def cdp_generate_query(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Generate a SQL query from a dataset definition."""
        result = await http_client.post(
            "config/queryGenerator",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
