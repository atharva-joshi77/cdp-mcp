"""
Workflow job tools for CDP Config API.

Implements 5 MCP tools: get job, rerun, kill, suspend, resume.
Source: acquia/cdp-configapi WorkflowController.java handleWorkflowActions
Job actions use: POST /v2/{tenantId}/config/workflows/{workflowId}?action=...&jobId=...
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_workflow_job_tools(server: FastMCP) -> None:
    """Register all workflow job tools on the MCP server."""

    @server.tool(
        name="cdp_get_workflow_job",
        description=(
            "Get details of a specific workflow job execution. "
            "Requires the workflow_id and job_id."
        ),
    )
    async def cdp_get_workflow_job(
        workflow_id: str,
        job_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get details of a specific workflow job execution."""
        result = await http_client.get(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"jobId": job_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_rerun_job",
        description="Re-run a completed or failed workflow job",
    )
    async def cdp_rerun_job(
        workflow_id: str,
        job_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Re-run a completed or failed workflow job."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "rerun", "jobId": job_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_kill_job",
        description="Kill a running workflow job",
    )
    async def cdp_kill_job(
        workflow_id: str,
        job_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Kill a running workflow job."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "kill", "jobId": job_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_suspend_job",
        description="Suspend a running workflow job",
    )
    async def cdp_suspend_job(
        workflow_id: str,
        job_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Suspend a running workflow job."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "suspend", "jobId": job_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_resume_job",
        description="Resume a suspended workflow job",
    )
    async def cdp_resume_job(
        workflow_id: str,
        job_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Resume a suspended workflow job."""
        result = await http_client.post(
            f"config/workflows/{workflow_id}",
            tenant_id=tenant_id,
            params={"action": "resume", "jobId": job_id},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
