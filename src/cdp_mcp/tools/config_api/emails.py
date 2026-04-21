"""
Email tools for CDP Config API.

Implements 1 MCP tool: send email.
Source: acquia/cdp-configapi EmailController.java
Endpoints: /v2/{tenantId}/config/emails/{emailType}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_email_tools(server: FastMCP) -> None:
    """Register email tools on the MCP server."""

    @server.tool(
        name="cdp_send_email",
        description=(
            "Send an email of a specific type. email_type examples: "
            "support, alert, notification. Pass email details as a JSON string."
        ),
    )
    async def cdp_send_email(
        email_type: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Send an email of a specific type."""
        result = await http_client.post(
            f"config/emails/{email_type}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
