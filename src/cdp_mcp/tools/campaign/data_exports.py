"""
Data-export tools for CDP Campaign API.

Source: acquia/cdp-campaignapi ExportDefController.java
Controller path: /v2/{tenantId}/export/dataexport

Implements the UI-verified sequence (ui-vega/src/app/main/dataExport):

  1. cdp_create_data_export  — POST export/dataexport?folderId=... (array body)
  2. cdp_update_data_export  — PUT  export/dataexport/{id}?folderId=...
  3. cdp_run_data_export     — POST config/workflows/DATA_EXPORT_DEFAULT
                                 ?action=run&entityType=exportDef&entityId=<id>
                                 body: {"dataExportProperties": "{}"}

Plus list / get / delete / copy helpers matching the Java controller.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client

_BASE = "export/dataexport"


def register_data_export_tools(server: FastMCP) -> None:
    """Register data-export tools on the MCP server."""

    @server.tool(
        name="cdp_list_data_exports",
        description="List all data export definitions for a tenant.",
    )
    async def cdp_list_data_exports(
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
        name="cdp_get_data_export",
        description="Get a specific data export definition by ID.",
    )
    async def cdp_get_data_export(
        export_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"{_BASE}/{export_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_data_export",
        description=(
            "Create a new data export definition. Body must be a JSON STRING "
            "containing at least `name` and `exportDefItems`. Pass folder_id to "
            "place the export in a specific folder (matches Vega UI which always "
            "sends ?folderId=). Controller expects an array, so the body you "
            "provide is wrapped in `[...]` automatically."
        ),
    )
    async def cdp_create_data_export(
        body: str,
        tenant_id: Optional[str] = None,
        folder_id: Optional[int] = None,
    ) -> str:
        export_def = json.loads(body)
        params: dict = {}
        if folder_id is not None:
            params["folderId"] = folder_id

        result = await http_client.post(
            _BASE,
            tenant_id=tenant_id,
            params=params or None,
            body=[export_def],
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_data_export",
        description=(
            "Update an existing data export definition. Pass updated fields as a "
            "JSON string. folder_id moves the export between folders."
        ),
    )
    async def cdp_update_data_export(
        export_id: int,
        body: str,
        tenant_id: Optional[str] = None,
        folder_id: Optional[int] = None,
    ) -> str:
        params: dict = {}
        if folder_id is not None:
            params["folderId"] = folder_id

        result = await http_client.put(
            f"{_BASE}/{export_id}",
            tenant_id=tenant_id,
            params=params or None,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_data_export",
        description="Delete a data export definition by ID.",
    )
    async def cdp_delete_data_export(
        export_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.delete(
            f"{_BASE}/{export_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Data export deleted successfully."

    @server.tool(
        name="cdp_copy_data_export",
        description="Copy/duplicate a data export definition by ID.",
    )
    async def cdp_copy_data_export(
        export_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            f"{_BASE}/{export_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_run_data_export",
        description=(
            "Execute a data export immediately via the DATA_EXPORT_DEFAULT workflow. "
            "Equivalent to clicking 'Send Now' in the Vega Data Export UI. "
            "Sends body `{\"dataExportProperties\":\"{}\"}` to match the UI contract."
        ),
    )
    async def cdp_run_data_export(
        export_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            "config/workflows/DATA_EXPORT_DEFAULT",
            tenant_id=tenant_id,
            params={
                "action": "run",
                "entityType": "exportDef",
                "entityId": str(export_id),
            },
            body={"dataExportProperties": "{}"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

