"""
GDPR/CCPA data erasure tools for CDP Data Warehouse API.

Implements 6 MCP tools: request, update, delete, admin status override, list statuses, get status by ID.
Source: acquia/cdp-dwapi PurgeController.java + DataErasureStatusController.java
Endpoints: /v2/{tenantId}/dw/dataerasure, /v2/{tenantId}/dw/dataerasure/admin, /v2/{tenantId}/dw/dataerasurestatus
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_data_erasure_tools(server: FastMCP) -> None:
    """Register all data erasure tools on the MCP server."""

    @server.tool(
        name="cdp_request_data_erasure",
        description=(
            "Request GDPR/CCPA data erasure for a customer "
            "(by identityHash or email). Pass erasure request as a JSON string."
        ),
    )
    async def cdp_request_data_erasure(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Request GDPR/CCPA data erasure for a customer."""
        result = await http_client.post(
            "dw/dataerasure",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_data_erasure_request",
        description="Cancel/delete a pending data erasure request",
    )
    async def cdp_delete_data_erasure_request(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Cancel/delete a pending data erasure request."""
        result = await http_client.delete(
            "dw/dataerasure",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Data erasure request cancelled successfully."

    @server.tool(
        name="cdp_update_data_erasure_request",
        description=(
            "Update an existing data erasure request (PUT /dw/dataerasure). "
            "Pass the updated erasure request body as a JSON string."
        ),
    )
    async def cdp_update_data_erasure_request(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing data erasure request."""
        result = await http_client.put(
            "dw/dataerasure",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_data_erasure_status_override",
        description=(
            "Admin-only: override the status of a data erasure request "
            "(POST /dw/dataerasure/admin?action=statusoverride). "
            "Pass override payload as JSON string."
        ),
    )
    async def cdp_data_erasure_status_override(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Admin-only data erasure status override."""
        result = await http_client.post(
            "dw/dataerasure/admin",
            tenant_id=tenant_id,
            params={"action": "statusoverride"},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_data_erasure_status",
        description="List all data erasure request statuses for a tenant",
    )
    async def cdp_get_data_erasure_status(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all data erasure request statuses for a tenant."""
        result = await http_client.get(
            "dw/dataerasurestatus",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_data_erasure_status_by_id",
        description="Get the status of a specific data erasure request by resource ID",
    )
    async def cdp_get_data_erasure_status_by_id(
        resource_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get the status of a specific data erasure request by resource ID."""
        result = await http_client.get(
            f"dw/dataerasurestatus/{resource_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
