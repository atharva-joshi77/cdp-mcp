"""
Campaign template tools for CDP Campaign API.

Implements 2 MCP tools: list templates, create template.
Source: acquia/cdp-campaignapi TemplateXrefController.java
Controller path: /v2/{tenantId}/campaign/templates
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_campaign_template_tools(server: FastMCP) -> None:
    """Register campaign template tools on the MCP server."""

    @server.tool(
        name="cdp_list_campaign_templates",
        description=(
            "List available campaign templates. "
            "Requires type parameter (e.g. PLAYBOOK, MESSAGE, AUDIENCE)."
        ),
    )
    async def cdp_list_campaign_templates(
        template_type: str = "PLAYBOOK",
        tenant_id: Optional[str] = None,
    ) -> str:
        """List available campaign templates."""
        result = await http_client.get(
            "campaign/templates",
            tenant_id=tenant_id,
            params={"type": template_type},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_campaign_template",
        description=(
            "Create a new campaign template. "
            "Pass template type and entityId along with tenant list as JSON body."
        ),
    )
    async def cdp_create_campaign_template(
        template_type: str,
        entity_id: int,
        tenant_ids: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create/update a campaign template cross-reference."""
        tenant_list = json.loads(tenant_ids)
        result = await http_client.put(
            "campaign/templates",
            tenant_id=tenant_id,
            params={"type": template_type, "entityId": entity_id},
            body=tenant_list,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
