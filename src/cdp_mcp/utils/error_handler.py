"""
Error normalization for CDP API responses.

Parses error response bodies into CDPError models and formats
them as human-readable strings for MCP tool responses.
"""

from __future__ import annotations

import httpx

from cdp_mcp.types.cdp_types import CDPError


async def parse_error_response(response: httpx.Response) -> CDPError:
    """
    Parse a CDP error response body into a CDPError.
    Falls back to a generic error if parsing fails.
    """
    try:
        body = response.json()
        if isinstance(body, dict) and "errorCode" in body and "userMessage" in body:
            return CDPError(**body)
        return CDPError(
            errorCode=f"HTTP_{response.status_code}",
            userMessage=body.get("message", "") or body.get("error", "") or response.reason_phrase or "",
            developerMessage=str(body),
        )
    except Exception:
        return CDPError(
            errorCode=f"HTTP_{response.status_code}",
            userMessage=response.reason_phrase or f"HTTP {response.status_code}",
            developerMessage=f"HTTP {response.status_code} {response.reason_phrase}",
        )


def format_error(error: CDPError | str) -> str:
    """Format a CDPError into a human-readable string for MCP tool responses."""
    if isinstance(error, str):
        return error
    parts = [
        f"Error {error.errorCode}: {error.userMessage}",
    ]
    if error.developerMessage:
        parts.append(f"Details: {error.developerMessage}")
    if error.moreInfo:
        parts.append(f"More info: {error.moreInfo}")
    return "\n".join(parts)
