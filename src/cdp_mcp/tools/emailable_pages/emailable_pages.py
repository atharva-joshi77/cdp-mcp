"""
Emailable Pages tools (cdp-emailable-pages-api).

Controller: EmailablePagesController
Base path : /v2/{tenantId}/emailablepages

Endpoints:
- GET    /                            — list pages
- GET    /{emailablePageId}           — get by id
- POST   /                            — create page
- PUT    /{emailablePageId}           — update page
- DELETE /{emailablePageId}           — soft-delete page
- POST   /{emailablePageId}           — restore soft-deleted page
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client

_BASE = "emailablepages"


def register_emailable_pages_tools(server: FastMCP) -> None:
    """Register emailable-pages tools on the MCP server."""

    @server.tool(
        name="cdp_list_emailable_pages",
        description="List emailable pages (GET /v2/{tenantId}/emailablepages).",
    )
    async def cdp_list_emailable_pages(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        result = await http_client.get(
            _BASE,
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_emailable_page",
        description="Get an emailable page by id (GET /v2/{tenantId}/emailablepages/{id}).",
    )
    async def cdp_get_emailable_page(
        page_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(f"{_BASE}/{page_id}", tenant_id=tenant_id)
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_emailable_page",
        description=(
            "Create an emailable page (POST /v2/{tenantId}/emailablepages). "
            "Pass the page definition as a JSON string."
        ),
    )
    async def cdp_create_emailable_page(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            _BASE, tenant_id=tenant_id, body=json.loads(body)
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_emailable_page",
        description=(
            "Update an emailable page (PUT /v2/{tenantId}/emailablepages/{id}). "
            "Pass the updated definition as a JSON string."
        ),
    )
    async def cdp_update_emailable_page(
        page_id: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.put(
            f"{_BASE}/{page_id}", tenant_id=tenant_id, body=json.loads(body)
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_emailable_page",
        description=(
            "Soft-delete an emailable page (DELETE /v2/{tenantId}/emailablepages/{id})."
        ),
    )
    async def cdp_delete_emailable_page(
        page_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.delete(f"{_BASE}/{page_id}", tenant_id=tenant_id)
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_restore_emailable_page",
        description=(
            "Restore a soft-deleted emailable page "
            "(POST /v2/{tenantId}/emailablepages/{id})."
        ),
    )
    async def cdp_restore_emailable_page(
        page_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(f"{_BASE}/{page_id}", tenant_id=tenant_id)
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

