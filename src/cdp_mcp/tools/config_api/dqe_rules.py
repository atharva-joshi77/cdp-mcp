"""
DQE (Data Quality Engine) rule tools for CDP Config API.

Implements 4 MCP tools: list/get DQE1 rules, list/get DQE2 rules.
Source: acquia/cdp-configapi DqeP1RuleController, DqeP2RuleController
Endpoints: /v2/{tenantId}/config/dqe1Rules, /v2/{tenantId}/config/dqe2Rules
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_dqe_rule_tools(server: FastMCP) -> None:
    """Register all DQE rule tools on the MCP server."""

    @server.tool(
        name="cdp_list_dqe1_rules",
        description="List DQE Phase 1 data quality rules",
    )
    async def cdp_list_dqe1_rules(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List DQE Phase 1 data quality rules."""
        result = await http_client.get(
            "config/dqe1Rules",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_dqe1_rule",
        description="Get a specific DQE Phase 1 rule by ID",
    )
    async def cdp_get_dqe1_rule(
        rule_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific DQE Phase 1 rule by ID."""
        result = await http_client.get(
            f"config/dqe1Rules/{rule_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_list_dqe2_rules",
        description="List DQE Phase 2 data quality rules",
    )
    async def cdp_list_dqe2_rules(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List DQE Phase 2 data quality rules."""
        result = await http_client.get(
            "config/dqe2Rules",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_dqe2_rule",
        description="Get a specific DQE Phase 2 rule by ID",
    )
    async def cdp_get_dqe2_rule(
        rule_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific DQE Phase 2 rule by ID."""
        result = await http_client.get(
            f"config/dqe2Rules/{rule_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
