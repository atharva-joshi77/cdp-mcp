"""
Global action tools for CDP APIs.

Implements 3 MCP tools: describe, clone, setCurrentVersion.
Source: apiSpecification/specs/globalActions.json

These actions are GENERIC — they work on any resource collection/instance
in the CDP API. The tool accepts a resourcePath parameter that specifies
which resource to act on (e.g., "report/widgets", "campaigndefs", "workflows").

Path style detection: Since different resources use different path styles
("v2" vs "none"), the tools accept an optional path_style parameter.
Default is "v2".

Notes:
- ?action=describe — POST on a collection or instance. Returns JSON Schema
  describing the resource (fields, types, editability).
- ?action=clone — POST on an instance. Creates a copy with a new ID.
- ?action=setCurrentVersion&version=N — POST on an instance. Rolls back
  to a previous version.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import PathStyle, http_client


def register_global_action_tools(server: FastMCP) -> None:
    """Register all global action tools on the MCP server."""

    @server.tool(
        name="cdp_describe_resource",
        description=(
            "Get the JSON Schema description of any CDP resource. "
            "Works on collections (e.g., 'report/widgets') or instances "
            "(e.g., 'report/widgets/123'). Returns field names, types, "
            "editability, and default page size for collections. "
            "Set path_style to 'none' for campaign/config/connector resources."
        ),
    )
    async def cdp_describe_resource(
        resource_path: str,
        tenant_id: Optional[str] = None,
        path_style: str = "v2",
    ) -> str:
        """Get the JSON Schema description of any CDP resource."""
        result = await http_client.post(
            resource_path,
            tenant_id=tenant_id,
            params={"action": "describe"},
            path_style=path_style,  # type: ignore[arg-type]
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_clone_resource",
        description=(
            "Clone any CDP resource instance. Creates a copy with a new ID "
            "and returns the cloned object. Works on any resource that "
            "supports versioning (campaigns, workflows, connectors, "
            "predictions, reports, etc.). "
            "The resource_path must include the ID, e.g. 'campaigndefs/123'. "
            "Set path_style to 'none' for campaign/config/connector resources."
        ),
    )
    async def cdp_clone_resource(
        resource_path: str,
        tenant_id: Optional[str] = None,
        path_style: str = "v2",
    ) -> str:
        """Clone any CDP resource instance."""
        result = await http_client.post(
            resource_path,
            tenant_id=tenant_id,
            params={"action": "clone"},
            path_style=path_style,  # type: ignore[arg-type]
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_set_current_version",
        description=(
            "Roll back any CDP resource to a specific version. "
            "Equivalent to GET version N then PUT as current. "
            "Returns the new version number. Works on any versioned resource. "
            "The resource_path must include the ID, e.g. 'workflows/456'. "
            "Set path_style to 'none' for campaign/config/connector resources."
        ),
    )
    async def cdp_set_current_version(
        resource_path: str,
        version: int,
        tenant_id: Optional[str] = None,
        path_style: str = "v2",
    ) -> str:
        """Roll back any CDP resource to a specific version."""
        result = await http_client.post(
            resource_path,
            tenant_id=tenant_id,
            params={"action": "setCurrentVersion", "version": version},
            path_style=path_style,  # type: ignore[arg-type]
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Version restored. Response: {json.dumps(result.data)}"
