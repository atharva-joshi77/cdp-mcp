"""
Password reset tools for CDP Security API.

Implements 3 MCP tools for AuthenticationResetController.
Source: acquia/cdp-security-service
       AuthenticationResetController at /authentication/reset

All endpoints are unauthenticated (@DisableAuthorization)
and accept a JSON body with username, resetCode, password, etc.
"""

from __future__ import annotations

import json

import httpx

from mcp.server.fastmcp import FastMCP

from cdp_mcp.config import get_base_url


def register_password_reset_tools(server: FastMCP) -> None:
    """Register password reset tools on the MCP server."""

    @server.tool(
        name="cdp_generate_password_reset",
        description=(
            "Generate a password reset link for a user. "
            "Sends a reset email to the user's registered address. "
            "Requires the username and source (VEGA or CONFIG)."
        ),
    )
    async def cdp_generate_password_reset(
        username: str,
        source: str = "VEGA",
    ) -> str:
        """POST /authentication/reset?action=generate"""
        base_url = get_base_url()
        url = f"{base_url}/authentication/reset?action=generate"

        body = {"username": username, "source": source}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={"Content-Type": "application/json"},
                content=json.dumps(body),
            )

        if not response.is_success:
            return f"Password reset generation failed ({response.status_code}): {response.text}"
        return "Password reset link generated and sent to the user's email."

    @server.tool(
        name="cdp_validate_password_reset",
        description=(
            "Validate a password reset code. "
            "Checks whether the reset code is still valid for the given user."
        ),
    )
    async def cdp_validate_password_reset(
        username: str,
        reset_code: str,
    ) -> str:
        """POST /authentication/reset?action=validate"""
        base_url = get_base_url()
        url = f"{base_url}/authentication/reset?action=validate"

        body = {"username": username, "resetCode": reset_code}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={"Content-Type": "application/json"},
                content=json.dumps(body),
            )

        if not response.is_success:
            return f"Reset code validation failed ({response.status_code}): {response.text}"
        return "Reset code is valid."

    @server.tool(
        name="cdp_update_password",
        description=(
            "Update a user's password using a valid reset code. "
            "Requires the username, reset code, and new password."
        ),
    )
    async def cdp_update_password(
        username: str,
        reset_code: str,
        new_password: str,
    ) -> str:
        """POST /authentication/reset?action=update"""
        base_url = get_base_url()
        url = f"{base_url}/authentication/reset?action=update"

        body = {
            "username": username,
            "resetCode": reset_code,
            "password": new_password,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={"Content-Type": "application/json"},
                content=json.dumps(body),
            )

        if not response.is_success:
            return f"Password update failed ({response.status_code}): {response.text}"
        return "Password updated successfully."
