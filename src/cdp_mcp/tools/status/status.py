"""
Status API tools for CDP (cdp-statusapi).

Covers three controllers:
- StatusApiController          GET /v2/{tid}/status/{resourceType}
- OrchestrationStatusController /v2/{tid}/orchstatus[/{id}[/log] | /connector/{connectorId}]
- DataPurgeStatusController     GET /v2/{tid}/purgestatus[?eventId=...]
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_status_tools(server: FastMCP) -> None:
    """Register status tools on the MCP server."""

    # ---------------------------------------------------------------- StatusApiController
    @server.tool(
        name="cdp_get_status_message",
        description=(
            "Get status messages for a workflow/entity event "
            "(GET /v2/{tenantId}/status/{resourceType}). "
            "resource_type defaults to 'statusmessage' (the only documented resource "
            "today) but the controller is generic — pass a different value if the "
            "platform exposes more resource types. "
            "Filters: event_type, entity_type, entity_id, workflow_id."
        ),
    )
    async def cdp_get_status_message(
        tenant_id: Optional[str] = None,
        resource_type: str = "statusmessage",
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> str:
        """Query status messages."""
        result = await http_client.get(
            f"status/{resource_type}",
            tenant_id=tenant_id,
            params={
                "eventType": event_type,
                "entityType": entity_type,
                "entityId": entity_id,
                "workflowId": workflow_id,
            },
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    # ------------------------------------------------------- OrchestrationStatusController
    @server.tool(
        name="cdp_list_orchestration_status",
        description=(
            "List orchestration statuses (GET /v2/{tenantId}/orchstatus). "
            "Returns workflow/connector orchestration runs and their state."
        ),
    )
    async def cdp_list_orchestration_status(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        result = await http_client.get(
            "orchstatus",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_orchestration_status",
        description=(
            "Get a single orchestration status record by id "
            "(GET /v2/{tenantId}/orchstatus/{id})."
        ),
    )
    async def cdp_get_orchestration_status(
        status_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"orchstatus/{status_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_orchestration_status_log",
        description=(
            "Fetch the log for an orchestration status record "
            "(GET /v2/{tenantId}/orchstatus/{id}/log)."
        ),
    )
    async def cdp_get_orchestration_status_log(
        status_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"orchstatus/{status_id}/log",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_orchestration_status_for_connector",
        description=(
            "Get orchestration status for a specific connector "
            "(GET /v2/{tenantId}/orchstatus/connector/{connectorId})."
        ),
    )
    async def cdp_get_orchestration_status_for_connector(
        connector_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"orchstatus/connector/{connector_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    # ---------------------------------------------------------- DataPurgeStatusController
    @server.tool(
        name="cdp_get_purge_status",
        description=(
            "Get data-purge status (GET /v2/{tenantId}/purgestatus). "
            "If event_id is supplied, returns status for that specific purge event."
        ),
    )
    async def cdp_get_purge_status(
        tenant_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            "purgestatus",
            tenant_id=tenant_id,
            params={"eventId": event_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
