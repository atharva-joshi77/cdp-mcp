"""
DatasetDef read tools for CDP Campaign API.

Source: acquia/cdp-campaignapi DatasetDefController.java
Controller path: /v2/{tenantId}/campaign/datasetDefs

DatasetDefs are the raw audience definition objects used inline by campaigns.
Most creation/update happens inline on a campaignDef (see campaign_playbook).
These tools expose read-only list/get helpers plus a generic `execute` action
for cases where the LLM needs to inspect an existing shared definition before
calling cdp_copy_datasetdef to detach it.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client

_BASE = "campaign/datasetDefs"


def register_dataset_def_tools(server: FastMCP) -> None:
    """Register datasetDef read tools on the MCP server."""

    @server.tool(
        name="cdp_list_dataset_defs",
        description=(
            "List datasetDefs (raw audience definitions) for a tenant. "
            "Useful for discovering shared definitions before calling "
            "cdp_copy_datasetdef."
        ),
    )
    async def cdp_list_dataset_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        lookup: Optional[str] = None,
    ) -> str:
        params: dict = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if lookup is not None:
            params["lookup"] = lookup

        result = await http_client.get(
            _BASE,
            tenant_id=tenant_id,
            params=params or None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_dataset_def",
        description="Get a specific datasetDef by ID.",
    )
    async def cdp_get_dataset_def(
        dataset_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"{_BASE}/{dataset_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

