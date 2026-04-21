"""
Content delivery tools for CDP Predictions API.

Implements 2 MCP tools: get prediction by container code, get web templates.
Source: acquia/cdp-predictions-api ContainerController.java + TemplateController.java
Endpoints: /v2/{tenantId}/content/containers/{containerCode}, /v2/{tenantId}/content/templates
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_content_tools(server: FastMCP) -> None:
    """Register content delivery tools on the MCP server."""

    @server.tool(
        name="cdp_get_prediction_container",
        description=(
            "Get a prediction result by container code. "
            "Optionally pass pid (person ID) and other query params."
        ),
    )
    async def cdp_get_prediction_container(
        container_code: str,
        tenant_id: Optional[str] = None,
        pid: Optional[str] = None,
    ) -> str:
        """Get a prediction result by container code."""
        params: dict = {}
        if pid is not None:
            params["pid"] = pid

        result = await http_client.get(
            f"content/containers/{container_code}",
            tenant_id=tenant_id,
            params=params if params else None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_web_templates",
        description="Get web personalization templates for a tenant",
    )
    async def cdp_get_web_templates(
        tenant_id: Optional[str] = None,
        payload: Optional[str] = None,
    ) -> str:
        """Get web personalization templates."""
        params: dict = {}
        if payload is not None:
            params["payload"] = payload

        result = await http_client.get(
            "content/templates",
            tenant_id=tenant_id,
            params=params if params else None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
