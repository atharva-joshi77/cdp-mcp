"""
Mailer REST API tools (cdp-mailer-rest-api).

Controllers (all under /v2/{tenantId}):
- MailerAccountController    /mailer/accounts     (soft-delete + restore)
- MailerSubUserController    /mailer/subusers     (soft-delete + restore)
- MailerIdentifierController /mailer/identifiers  (+ /campaign/{c}/dispatch/{d})
- MailerBatchController      /mailer/batches      (+ POST /{id} to process a batch)

The two soft-delete controllers share the same shape (list/get/create/update/
delete/restore); the two plain controllers share list/get/create/update and
then add their own custom sub-resources.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


# -------------------------------------------------------------------- helpers


def _register_crud(
    server: FastMCP,
    *,
    resource: str,
    singular: str,
    plural: str,
    include_soft_delete: bool,
) -> None:
    """Register standard list/get/create/update (+ optional delete/restore) tools."""
    base = f"mailer/{resource}"

    @server.tool(
        name=f"cdp_list_mailer_{resource}",
        description=f"List mailer {plural} (GET /v2/{{tenantId}}/{base}).",
    )
    async def _list(  # noqa: D401
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        result = await http_client.get(
            base, tenant_id=tenant_id, params={"offset": offset, "limit": limit}
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name=f"cdp_get_mailer_{singular}",
        description=f"Get a mailer {singular} by id (GET /v2/{{tenantId}}/{base}/{{id}}).",
    )
    async def _get(  # noqa: D401
        id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(f"{base}/{id}", tenant_id=tenant_id)
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name=f"cdp_create_mailer_{singular}",
        description=(
            f"Create a mailer {singular} (POST /v2/{{tenantId}}/{base}). "
            "Pass the definition as a JSON string."
        ),
    )
    async def _create(  # noqa: D401
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            base, tenant_id=tenant_id, body=json.loads(body)
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name=f"cdp_update_mailer_{singular}",
        description=(
            f"Update a mailer {singular} (PUT /v2/{{tenantId}}/{base}/{{id}}). "
            "Pass the updated definition as a JSON string."
        ),
    )
    async def _update(  # noqa: D401
        id: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.put(
            f"{base}/{id}", tenant_id=tenant_id, body=json.loads(body)
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    if include_soft_delete:

        @server.tool(
            name=f"cdp_delete_mailer_{singular}",
            description=(
                f"Soft-delete a mailer {singular} "
                f"(DELETE /v2/{{tenantId}}/{base}/{{id}})."
            ),
        )
        async def _delete(  # noqa: D401
            id: str,
            tenant_id: Optional[str] = None,
        ) -> str:
            result = await http_client.delete(f"{base}/{id}", tenant_id=tenant_id)
            if not result.success:
                return f"Error: {format_error(result.error)}"
            return json.dumps(result.data, indent=2)

        @server.tool(
            name=f"cdp_restore_mailer_{singular}",
            description=(
                f"Restore a soft-deleted mailer {singular} "
                f"(POST /v2/{{tenantId}}/{base}/{{id}})."
            ),
        )
        async def _restore(  # noqa: D401
            id: str,
            tenant_id: Optional[str] = None,
        ) -> str:
            result = await http_client.post(f"{base}/{id}", tenant_id=tenant_id)
            if not result.success:
                return f"Error: {format_error(result.error)}"
            return json.dumps(result.data, indent=2)


# ---------------------------------------------------------------- registration


def register_mailer_tools(server: FastMCP) -> None:
    """Register all cdp-mailer-rest-api tools on the MCP server."""

    # Standard CRUD for the four resources.
    _register_crud(
        server,
        resource="accounts",
        singular="account",
        plural="accounts",
        include_soft_delete=True,
    )
    _register_crud(
        server,
        resource="subusers",
        singular="subuser",
        plural="subusers",
        include_soft_delete=True,
    )
    _register_crud(
        server,
        resource="identifiers",
        singular="identifier",
        plural="identifiers",
        include_soft_delete=False,
    )
    _register_crud(
        server,
        resource="batches",
        singular="batch",
        plural="batches",
        include_soft_delete=False,
    )

    # MailerIdentifierController extra endpoint:
    # GET /mailer/identifiers/campaign/{campaignId}/dispatch/{dispatchId}
    @server.tool(
        name="cdp_get_mailer_identifier_by_campaign_dispatch",
        description=(
            "Look up a mailer identifier by campaign + dispatch "
            "(GET /v2/{tenantId}/mailer/identifiers/campaign/{campaignId}"
            "/dispatch/{dispatchId})."
        ),
    )
    async def cdp_get_mailer_identifier_by_campaign_dispatch(
        campaign_id: str,
        dispatch_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"mailer/identifiers/campaign/{campaign_id}/dispatch/{dispatch_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    # MailerBatchController extra endpoint:
    # POST /mailer/batches/{id} — process/trigger a batch.
    @server.tool(
        name="cdp_process_mailer_batch",
        description=(
            "Trigger processing of a mailer batch by id "
            "(POST /v2/{tenantId}/mailer/batches/{id}). "
            "Optional JSON body is forwarded as-is."
        ),
    )
    async def cdp_process_mailer_batch(
        batch_id: str,
        tenant_id: Optional[str] = None,
        body: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            f"mailer/batches/{batch_id}",
            tenant_id=tenant_id,
            body=json.loads(body) if body else None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

