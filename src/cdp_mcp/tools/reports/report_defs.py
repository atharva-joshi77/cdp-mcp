"""
Report definition tools for CDP Report API.

Implements 7 MCP tools: list, create, get, update, delete, copy report definitions
plus Excel pivot export.
Source: acquia/cdp-campaignapi ReportDefController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/reportDefs

Notes:
- reportType must be "CUBE" (uses cubicSetDef) or "RELATIONAL" (uses datasetOperation)
- ?action=exportExcelPivot — POST on collection with cubeId query param and body {password}
- ?action=copy — POST on instance to duplicate
- Collection POST accepts arrays — single objects are wrapped in an array
- Report execution/fetch are through the DW API (dw/report), not here
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_report_def_tools(server: FastMCP) -> None:
    """Register all report definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_report_defs",
        description="List all report definitions for a tenant",
    )
    async def cdp_list_report_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all report definitions for a tenant."""
        result = await http_client.get(
            "report/reportDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_report_def",
        description=(
            "Create a new report definition. Pass definition as a JSON string. "
            "Requires name and reportType ('CUBE' or 'RELATIONAL'). "
            "CUBE type uses cubicSetDef, RELATIONAL uses datasetOperation."
        ),
    )
    async def cdp_create_report_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new report definition. API expects an array — wraps single object."""
        report_def = json.loads(body)
        payload = report_def if isinstance(report_def, list) else [report_def]

        result = await http_client.post(
            "report/reportDefs",
            tenant_id=tenant_id,
            body=payload,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_report_def",
        description=(
            "Get a report definition by ID. Returns full definition "
            "including reportType, datasetOperation or cubicSetDef."
        ),
    )
    async def cdp_get_report_def(
        report_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a report definition by ID."""
        result = await http_client.get(
            f"report/reportDefs/{report_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_report_def",
        description="Update an existing report definition by ID. Pass updated fields as a JSON string.",
    )
    async def cdp_update_report_def(
        report_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing report definition by ID."""
        result = await http_client.put(
            f"report/reportDefs/{report_def_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_report_def",
        description="Delete a report definition by ID",
    )
    async def cdp_delete_report_def(
        report_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a report definition by ID."""
        result = await http_client.delete(
            f"report/reportDefs/{report_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"ReportDef {report_def_id} deleted successfully."

    @server.tool(
        name="cdp_copy_report_def",
        description="Copy a report definition by ID. Creates a duplicate of the report.",
    )
    async def cdp_copy_report_def(
        report_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Copy a report definition by ID."""
        result = await http_client.post(
            f"report/reportDefs/{report_def_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_export_report_excel",
        description=(
            "Export a report as an Excel pivot file. "
            "Requires cubeId and password. The export is generated from "
            "the cube data on the collection endpoint."
        ),
    )
    async def cdp_export_report_excel(
        cube_id: str,
        password: str,
        tenant_id: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> str:
        """Export a report as an Excel pivot file."""
        body: dict = {"password": password}
        if filename is not None:
            body["filename"] = filename

        result = await http_client.post(
            "report/reportDefs",
            tenant_id=tenant_id,
            params={"action": "exportExcelPivot", "cubeId": cube_id},
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Excel export initiated. Response: {json.dumps(result.data)}"
