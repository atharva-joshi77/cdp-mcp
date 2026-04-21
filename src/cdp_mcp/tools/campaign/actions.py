"""
Campaign lifecycle action tools for CDP Campaign API.

Implements 4 MCP tools: start (run now), publish (web/triggered), stop (kill),
copy an existing datasetDef (safety helper for the "no shared datasetDefs" rule).

Source mapping (verified against cdp-campaignapi + cdp-configapi + ui-vega):
  - POST /v2/{tenantId}/campaign/campaignDefs/run?cohort=<bool>&entityId=<id>
        body: {"campaignProperties": "{}"}                       — one-shot "send now"
  - POST /v2/{tenantId}/config/workflows/CAMPAIGN_FLOW_DEFAULT?action=run
            &entityType=campaign&entityId=<id>
        body: {"campaignProperties": "{\"webAction\":\"PUBLISH\"}"}  — publish web/triggered
  - POST /v2/{tenantId}/campaign/campaignDefs/{id}/workflow/kill
  - POST /v2/{tenantId}/campaign/datasetDefs/{id}?action=copy      — safety helper
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_campaign_action_tools(server: FastMCP) -> None:
    """Register campaign lifecycle action tools on the MCP server."""

    @server.tool(
        name="cdp_start_campaign",
        description=(
            "Execute/run a campaign immediately ('send now'). Requires entity_id "
            "(the campaign def resourceId). Set cohort=True for cohort campaigns. "
            "An empty `{\"campaignProperties\":\"{}\"}` body is sent automatically to "
            "match the Vega UI contract — omitting it causes the backend to 400 on "
            "some builds. For triggered/web campaigns use cdp_publish_web_campaign "
            "instead."
        ),
    )
    async def cdp_start_campaign(
        entity_id: str,
        tenant_id: Optional[str] = None,
        version: Optional[int] = None,
        cohort: Optional[bool] = None,
    ) -> str:
        """Execute/run a campaign via the workflow engine."""
        params: dict = {"entityId": entity_id}
        if version is not None:
            params["version"] = version
        if cohort is not None:
            # Query string serialization needs lowercase json-style bool
            params["cohort"] = "true" if cohort else "false"

        result = await http_client.post(
            "campaign/campaignDefs/run",
            tenant_id=tenant_id,
            params=params,
            body={"campaignProperties": "{}"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_publish_web_campaign",
        description=(
            "Publish a triggered/web campaign via the CAMPAIGN_FLOW_DEFAULT workflow. "
            "This is the correct action for real-time/triggered campaigns (web, API, "
            "journey) — cdp_start_campaign only works for batch 'send now' runs. "
            "Mirrors what the Vega UI does when you click 'Publish' on a web campaign."
        ),
    )
    async def cdp_publish_web_campaign(
        entity_id: str,
        tenant_id: Optional[str] = None,
        web_action: str = "PUBLISH",
    ) -> str:
        """Publish a triggered/web campaign via CAMPAIGN_FLOW_DEFAULT."""
        result = await http_client.post(
            "config/workflows/CAMPAIGN_FLOW_DEFAULT",
            tenant_id=tenant_id,
            params={
                "action": "run",
                "entityType": "campaign",
                "entityId": entity_id,
            },
            body={"campaignProperties": json.dumps({"webAction": web_action})},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_stop_campaign",
        description="Stop/kill a running campaign by ID. Sends a workflow kill signal.",
    )
    async def cdp_stop_campaign(
        campaign_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Stop a running campaign by killing its workflow."""
        result = await http_client.post(
            f"campaign/campaignDefs/{campaign_id}/workflow/kill",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_copy_datasetdef",
        description=(
            "Copy an existing datasetDef (audience definition) to create a new, "
            "independent one. CDP rejects shared datasetDefs across campaigns with "
            "E400: 'The campaignDef being created refers to an existing datasetDef. "
            "Please correct this by calling /v2/{tenantId}/datasetDef/{id}?action=copy'. "
            "Use this tool to produce a detached copy, then embed the returned object "
            "inline in your new campaign's `audience` field."
        ),
    )
    async def cdp_copy_datasetdef(
        dataset_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Copy an existing datasetDef to produce a new independent one."""
        result = await http_client.post(
            f"campaign/datasetDefs/{dataset_def_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
