"""
Query Language (QL) tools for CDP QL API.

Implements 2 MCP tools: SQL query via GET and SQL query via POST.
Source: apiSpecification/specs/qlAPI.json
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/ql

Notes:
- The QL API supports read-only Impala SQL only. UPDATE/INSERT/DROP/ALTER are not supported.
- GET: query is passed as ?query= param. Use for short queries.
- POST: query is in request body as {"query": "SELECT ..."}. Use for long queries.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_query_language_tools(server: FastMCP) -> None:
    """Register all query language tools on the MCP server."""

    @server.tool(
        name="cdp_query_sql",
        description=(
            "Execute a read-only SQL query against the CDP data warehouse (Impala SQL) "
            "using GET with query in URL. Suitable for short queries. "
            "For long queries, use cdp_query_sql_post instead. "
            "Only SELECT statements are supported."
        ),
    )
    async def cdp_query_sql(
        query: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Execute a read-only SQL query via GET."""
        result = await http_client.get(
            "ql",
            tenant_id=tenant_id,
            params={"query": query},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_query_sql_post",
        description=(
            "Execute a read-only SQL query via POST body. "
            "Use this for long queries that may exceed URL length limits. "
            "Only SELECT statements are supported."
        ),
    )
    async def cdp_query_sql_post(
        query: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Execute a read-only SQL query via POST."""
        result = await http_client.post(
            "ql",
            tenant_id=tenant_id,
            body={"query": query},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
