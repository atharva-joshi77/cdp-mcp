"""
Schedule tools for CDP Config API.

Implements 7 MCP tools: list, get, create, update, delete, activate, deactivate.
Source: acquia/cdp-configapi ScheduleController.java
Endpoints: /v2/{tenantId}/config/schedules

The CRUD tools mirror the UI's canonical schedule lifecycle observed in
ui-core `ScheduleService.save()` and `ConnectorDataService.createSchedule()`:
    1. Look up workflow by name -> take its numeric DB `id` (NOT the string
       workflowId). This value becomes `referenceId` on the schedule.
    2. POST /config/schedules with a full schedule body (see
       `cdp_create_schedule` for the canonical shape).
    3. POST /config/workflows/{workflowName}?action=schedule&scheduleId=...
       to register the schedule with the workflow runner
       (`cdp_invoke_workflow_action`).

Activation/deactivation of an existing schedule is done via workflow actions
(action=activate_schedule / deactivate_schedule). Deletion is a plain
DELETE /config/schedules/{id}, but the UI ALSO fires
`action=unschedule&scheduleId=...` on the workflow first — use
`cdp_invoke_workflow_action` for that step.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_schedule_tools(server: FastMCP) -> None:
    """Register all schedule tools on the MCP server."""

    @server.tool(
        name="cdp_list_schedules",
        description=(
            "List schedules for a tenant. "
            "Requires a schedule type (e.g. 'workflow'). "
            "Optionally filter by entityType and entityId."
        ),
    )
    async def cdp_list_schedules(
        schedule_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List schedules for a tenant."""
        params: dict = {"type": schedule_type, "offset": offset, "limit": limit}
        if entity_type is not None:
            params["entityType"] = entity_type
        if entity_id is not None:
            params["entityId"] = entity_id
        result = await http_client.get(
            "config/schedules",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_schedule",
        description="Get a specific schedule by ID",
    )
    async def cdp_get_schedule(
        schedule_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific schedule by ID."""
        result = await http_client.get(
            f"config/schedules/{schedule_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_activate_schedule",
        description=(
            "Activate a schedule. This triggers the schedule's workflow action "
            "via the workflow controller."
        ),
    )
    async def cdp_activate_schedule(
        workflow_id: str,
        schedule_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Activate a schedule via the workflow action handler."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "activate_schedule", "scheduleId": schedule_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_deactivate_schedule",
        description=(
            "Deactivate a schedule. This triggers the schedule's workflow action "
            "via the workflow controller."
        ),
    )
    async def cdp_deactivate_schedule(
        workflow_id: str,
        schedule_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Deactivate a schedule via the workflow action handler."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "deactivate_schedule", "scheduleId": schedule_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_schedule",
        description=(
            "Create a new schedule row in config/schedules. "
            "`body` is a JSON string of the schedule body. Canonical shape "
            "(from ui-core ScheduleService.save):\n"
            '{\n'
            '  \"type\": \"WORKFLOW\",\n'
            '  \"referenceId\": <numeric workflow.id from GET config/workflows/{name}>,\n'
            '  \"entityType\": \"connector\" | \"campaign\" | \"report\" | \"exportDef\" | ...,\n'
            '  \"entityId\": <resource id>,\n'
            '  \"scheduleName\": \"Schedule-<unique>\",\n'
            '  \"active\": true,\n'
            '  \"period\": \"HOURS\" | \"DAYS\" | \"WEEKS\" | \"MONTHS\" | \"MINUTES\",\n'
            '  \"frequency\": 1,\n'
            '  \"startTime\": \"00:00\",\n'
            '  \"startTimestamp\": \"YYYY-MM-DDTHH:mm\",\n'
            '  \"timeZone\": \"America/New_York\",\n'
            '  \"jobData\": {\"campaignProperties\": \"{}\"}  // optional, workflow-specific\n'
            '}\n'
            "After creating the row, call cdp_invoke_workflow_action with "
            "action='schedule' and the returned scheduleId to arm it."
        ),
    )
    async def cdp_create_schedule(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a schedule."""
        result = await http_client.post(
            "config/schedules",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_schedule",
        description=(
            "Update an existing schedule row (PUT config/schedules/{id}). "
            "`body` is a JSON string of the full schedule body — see "
            "cdp_create_schedule for the canonical shape. Pass the same "
            "`referenceId`, `entityType`, `entityId` as the original, or the "
            "CDP backend will detach the schedule from its workflow."
        ),
    )
    async def cdp_update_schedule(
        schedule_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update a schedule."""
        result = await http_client.put(
            f"config/schedules/{schedule_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_schedule",
        description=(
            "Delete a schedule (DELETE config/schedules/{id}). "
            "IMPORTANT: the UI fires cdp_invoke_workflow_action(action="
            "'unschedule', scheduleId=...) FIRST to detach the schedule from "
            "its runner workflow; doing only the DELETE leaves a dangling "
            "trigger registration in some workflows (AIF_RUNNER, "
            "REPORT_RUNNNER_DEFAULT). See the orchestration playbook."
        ),
    )
    async def cdp_delete_schedule(
        schedule_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a schedule."""
        result = await http_client.delete(
            f"config/schedules/{schedule_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

