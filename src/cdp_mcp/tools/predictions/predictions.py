"""
Prediction definition tools for CDP (Campaign API).

Implements 6 MCP tools: list, get, create, update, delete, clone prediction
definitions.

Source of truth: `cdp-campaignapi/src/main/java/com/agilone/api/prediction/
controller/PredictionDefController.java`

Controller: `@RequestMapping("/v2/{tenantId}/campaign/predictionDefs")`
  - GET    /                         -> list
  - GET    /{id}                     -> get
  - POST   /                         -> create
  - PUT    /{id}                     -> update
  - DELETE /{id}                     -> delete
  - POST   /{id}?action=copy         -> clone

NOTE (P0 audit fix, 2026-04-20): the previous version of this module targeted
`/{tenantId}/prediction/predictiondefs` with `path_style="none"`, which does
not exist on any CDP service. It also exposed `publish`, `unpublish`, and
`execute` tools whose corresponding `action=publish|unpublish|getPrediction`
endpoints do not exist on `PredictionDefController`. Those tools have been
removed. If/when dedicated prediction-execution endpoints are re-introduced,
they should be added back against the correct controller.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client

# Base path relative to the tenant segment (default "v2" path_style ->
# full URL becomes /v2/{tenantId}/campaign/predictionDefs).
_BASE = "campaign/predictionDefs"


def register_prediction_tools(server: FastMCP) -> None:
    """Register prediction-definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_predictions",
        description=(
            "List prediction definitions for a tenant "
            "(GET /v2/{tenantId}/campaign/predictionDefs). "
            "Pass `q` (e.g. 'isPublished:true') for server-side filtering."
        ),
    )
    async def cdp_list_predictions(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        q: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            _BASE,
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit, "q": q},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_prediction",
        description="Get a specific prediction definition by ID (GET /v2/{tenantId}/campaign/predictionDefs/{id}).",
    )
    async def cdp_get_prediction(
        prediction_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"{_BASE}/{prediction_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_prediction",
        description=(
            "Create a new prediction definition "
            "(POST /v2/{tenantId}/campaign/predictionDefs). "
            "Pass the full definition as a JSON string."
        ),
    )
    async def cdp_create_prediction(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            return f"Error: `body` must be a valid JSON string ({exc})."
        result = await http_client.post(
            _BASE,
            tenant_id=tenant_id,
            body=parsed,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_prediction",
        description=(
            "Update an existing prediction definition "
            "(PUT /v2/{tenantId}/campaign/predictionDefs/{id}). "
            "Pass updated fields as a JSON string."
        ),
    )
    async def cdp_update_prediction(
        prediction_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            return f"Error: `body` must be a valid JSON string ({exc})."
        result = await http_client.put(
            f"{_BASE}/{prediction_def_id}",
            tenant_id=tenant_id,
            body=parsed,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_prediction",
        description="Delete a prediction definition (DELETE /v2/{tenantId}/campaign/predictionDefs/{id}).",
    )
    async def cdp_delete_prediction(
        prediction_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.delete(
            f"{_BASE}/{prediction_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Prediction definition deleted successfully."

    @server.tool(
        name="cdp_clone_prediction",
        description=(
            "Clone a prediction definition — creates a copy with a new ID "
            "(POST /v2/{tenantId}/campaign/predictionDefs/{id}?action=copy)."
        ),
    )
    async def cdp_clone_prediction(
        prediction_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            f"{_BASE}/{prediction_def_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
