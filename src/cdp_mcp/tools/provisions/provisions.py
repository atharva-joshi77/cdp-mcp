"""
Self-Service Provisioning tools for CDP.

Implements MCP tools for provisioning services, instances, limits, and connector links.
Endpoints under /v2/{tenantId}/provisions/{services|instances|limits|links}.
Source: Documentation - self-service-api.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def _ok(result) -> str:
    if not result.success:
        return f"Error: {format_error(result.error)}"
    return json.dumps(result.data, indent=2) if result.data is not None else "OK"


def register_provisions_tools(server: FastMCP) -> None:
    """Register self-service provisioning tools on the MCP server."""

    # ---- Provisioning Services ----

    @server.tool(
        name="cdp_list_provision_services",
        description="List available provision services for a tenant (paged).",
    )
    async def cdp_list_provision_services(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        result = await http_client.get(
            "provisions/services",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        return _ok(result)

    @server.tool(
        name="cdp_get_provision_service",
        description=(
            "Get a specific provision service by ID or name "
            "(GET /provisions/services/{serviceId|serviceName})."
        ),
    )
    async def cdp_get_provision_service(
        service_id_or_name: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"provisions/services/{service_id_or_name}",
            tenant_id=tenant_id,
        )
        return _ok(result)

    # ---- Provisioning Instances ----

    @server.tool(
        name="cdp_list_provision_instances",
        description=(
            "List provisioned instances with optional filters: "
            "active, status, provision_name, requested_by."
        ),
    )
    async def cdp_list_provision_instances(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        status: Optional[str] = None,
        provision_name: Optional[str] = None,
        requested_by: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            "provisions/instances",
            tenant_id=tenant_id,
            params={
                "offset": offset,
                "limit": limit,
                "active": active,
                "status": status,
                "provisionName": provision_name,
                "requestedBy": requested_by,
            },
        )
        return _ok(result)

    @server.tool(
        name="cdp_get_provision_instance",
        description="Get a specific provisioned instance by ID.",
    )
    async def cdp_get_provision_instance(
        instance_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"provisions/instances/{instance_id}",
            tenant_id=tenant_id,
        )
        return _ok(result)

    @server.tool(
        name="cdp_get_mapped_provision_instance",
        description=(
            "Get a mapped provisioned resource by instance ID "
            "(GET /provisions/instances/mapped/{instanceId})."
        ),
    )
    async def cdp_get_mapped_provision_instance(
        instance_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            f"provisions/instances/mapped/{instance_id}",
            tenant_id=tenant_id,
        )
        return _ok(result)

    @server.tool(
        name="cdp_list_unlinked_provision_instances",
        description=(
            "List unlinked provisioned instances for a connector class and type "
            "(GET /provisions/instances/unlinked?connectorClassName=&connectorType=)."
        ),
    )
    async def cdp_list_unlinked_provision_instances(
        connector_class_name: str,
        connector_type: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            "provisions/instances/unlinked",
            tenant_id=tenant_id,
            params={
                "connectorClassName": connector_class_name,
                "connectorType": connector_type,
            },
        )
        return _ok(result)

    @server.tool(
        name="cdp_create_provision_instance",
        description=(
            "Provision a new instance (POST /provisions/instances). "
            "Pass request body as JSON string with serviceId, provisionName, etc."
        ),
    )
    async def cdp_create_provision_instance(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            "provisions/instances",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        return _ok(result)

    @server.tool(
        name="cdp_update_provision_instance",
        description=(
            "Modify a provisioned instance (PUT /provisions/instances/{id}). "
            "Pass update body as JSON string."
        ),
    )
    async def cdp_update_provision_instance(
        instance_id: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.put(
            f"provisions/instances/{instance_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        return _ok(result)

    @server.tool(
        name="cdp_provision_instance_action",
        description=(
            "Perform an action on a provision instance "
            "(POST /provisions/instances/{id}?action=...). "
            "Actions: regenerate_credentials, apply_policy_change. "
            "Pass optional body as JSON string (required for apply_policy_change)."
        ),
    )
    async def cdp_provision_instance_action(
        instance_id: str,
        action: str,
        body: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            f"provisions/instances/{instance_id}",
            tenant_id=tenant_id,
            params={"action": action},
            body=json.loads(body) if body else None,
        )
        return _ok(result)

    @server.tool(
        name="cdp_deactivate_provision_instance",
        description="Deactivate a provisioned instance (DELETE /provisions/instances/{id}).",
    )
    async def cdp_deactivate_provision_instance(
        instance_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.delete(
            f"provisions/instances/{instance_id}",
            tenant_id=tenant_id,
        )
        return _ok(result)

    @server.tool(
        name="cdp_deprovision_instance",
        description=(
            "Deprovision a provisioned instance "
            "(DELETE /provisions/instances/deprovision/{id})."
        ),
    )
    async def cdp_deprovision_instance(
        instance_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.delete(
            f"provisions/instances/deprovision/{instance_id}",
            tenant_id=tenant_id,
        )
        return _ok(result)

    @server.tool(
        name="cdp_retry_provision_instance",
        description=(
            "Retry provisioning a failed instance "
            "(POST /provisions/instances/retry-provision/{id}). "
            "Pass same body as initial provisioning as JSON string."
        ),
    )
    async def cdp_retry_provision_instance(
        instance_id: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            f"provisions/instances/retry-provision/{instance_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        return _ok(result)

    @server.tool(
        name="cdp_reactivate_provision_instance",
        description=(
            "Reactivate a deactivated instance "
            "(POST /provisions/instances/reactivate/{id})."
        ),
    )
    async def cdp_reactivate_provision_instance(
        instance_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.post(
            f"provisions/instances/reactivate/{instance_id}",
            tenant_id=tenant_id,
        )
        return _ok(result)

    # ---- Provisioning Limits ----

    @server.tool(
        name="cdp_list_provision_limits",
        description="Fetch provisioning limits for all services of a tenant.",
    )
    async def cdp_list_provision_limits(
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            "provisions/limits",
            tenant_id=tenant_id,
        )
        return _ok(result)

    @server.tool(
        name="cdp_get_provision_limit",
        description=(
            "Get provisioning limit for a specific service "
            "(GET /provisions/limits/{serviceId}). "
            "Set validate=true to include a 'provisioningAllowed' flag."
        ),
    )
    async def cdp_get_provision_limit(
        service_id: str,
        tenant_id: Optional[str] = None,
        validate: Optional[bool] = None,
    ) -> str:
        result = await http_client.get(
            f"provisions/limits/{service_id}",
            tenant_id=tenant_id,
            params={"action": "validate"} if validate else None,
        )
        return _ok(result)

    # ---- Connector Links ----

    @server.tool(
        name="cdp_list_connector_links",
        description="Fetch all connector links (GET /provisions/links).",
    )
    async def cdp_list_connector_links(
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            "provisions/links",
            tenant_id=tenant_id,
        )
        return _ok(result)

    @server.tool(
        name="cdp_list_connector_links_by_class",
        description=(
            "Fetch connector links filtered by connector class "
            "(GET /provisions/links/connector-class?connectorClass=...)."
        ),
    )
    async def cdp_list_connector_links_by_class(
        connector_class: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        result = await http_client.get(
            "provisions/links/connector-class",
            tenant_id=tenant_id,
            params={"connectorClass": connector_class},
        )
        return _ok(result)
