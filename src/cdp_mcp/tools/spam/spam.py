"""
Spam scoring tool for CDP.

Implements 1 MCP tool: score email/message content for spam likelihood.
Endpoint: POST /v2/{tenantId}/spam/score
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_spam_tools(server: FastMCP) -> None:
    """Register spam scoring tools on the MCP server."""

    @server.tool(
        name="cdp_score_spam",
        description=(
            "Score email/message content for spam likelihood "
            "(POST /v2/{tenantId}/spam/score). The request body MUST be a JSON ARRAY: "
            "[{\"subject\": \"...\", \"body\": \"...\", \"fromAddress\": \"...\", \"fromName\": \"...\"}]. "
            "Passing a single object returns E400 'Cannot deserialize from Object value'. "
            "Pass the array as a JSON string."
        ),
    )
    async def cdp_score_spam(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Score message content for spam."""
        result = await http_client.post(
            "spam/score",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
