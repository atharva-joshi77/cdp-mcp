"""
Cache operations tools for CDP Cache API.

Implements 9 MCP tools: GET/PUT/DELETE by key, by ID, and by group+ID.
Source: apiSpecification/specs/cacheAPI.yaml
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/cache/...

Notes:
- cacheType must be "in_memory" (volatile, fast) or "persistent" (durable)
- Three access patterns:
  - By key:   cache/{cacheType}/key/{cacheKey}
  - By ID:    cache/{cacheType}/id/{id}         (auto-generated key)
  - By group: cache/{cacheType}/group/{group}/id/{id}
- PUT operations accept {value: string, expiryTime?: int}
- GET returns {key, value, tenantId}
- DELETE returns 204 on success
"""

from __future__ import annotations

import json
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client

# Cache type: in_memory (volatile, fast) or persistent (durable)
CacheType = Literal["in_memory", "persistent"]


def register_cache_tools(server: FastMCP) -> None:
    """Register all cache operation tools on the MCP server."""

    # ═══════════════════════════════════════════════════════════════
    # BY KEY — cache/{cacheType}/key/{cacheKey}
    # ═══════════════════════════════════════════════════════════════

    @server.tool(
        name="cdp_cache_get_by_key",
        description=(
            "Get a cached value by explicit cache key. "
            "Returns the stored value string and metadata."
        ),
    )
    async def cdp_cache_get_by_key(
        cache_type: str,
        cache_key: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a cached value by explicit cache key."""
        result = await http_client.get(
            f"cache/{cache_type}/key/{cache_key}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_cache_put_by_key",
        description=(
            "Set or update a cache entry by explicit key. "
            "Value is stored as a string. Optional expiryTime in seconds."
        ),
    )
    async def cdp_cache_put_by_key(
        cache_type: str,
        cache_key: str,
        value: str,
        tenant_id: Optional[str] = None,
        expiry_time: Optional[int] = None,
    ) -> str:
        """Set or update a cache entry by explicit key."""
        body: dict = {"value": value}
        if expiry_time is not None:
            body["expiryTime"] = expiry_time

        result = await http_client.put(
            f"cache/{cache_type}/key/{cache_key}",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_cache_delete_by_key",
        description="Delete a cache entry by explicit key. Returns 204 on success.",
    )
    async def cdp_cache_delete_by_key(
        cache_type: str,
        cache_key: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a cache entry by explicit key."""
        result = await http_client.delete(
            f"cache/{cache_type}/key/{cache_key}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Cache entry '{cache_key}' deleted from {cache_type}."

    # ═══════════════════════════════════════════════════════════════
    # BY ID — cache/{cacheType}/id/{id}
    # ═══════════════════════════════════════════════════════════════

    @server.tool(
        name="cdp_cache_get_by_id",
        description=(
            "Get a cached value by ID. "
            "The cache key is auto-generated using the ID and any query parameters."
        ),
    )
    async def cdp_cache_get_by_id(
        cache_type: str,
        id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a cached value by ID."""
        result = await http_client.get(
            f"cache/{cache_type}/id/{id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_cache_put_by_id",
        description="Set or update a cache entry by ID. The cache key is auto-generated.",
    )
    async def cdp_cache_put_by_id(
        cache_type: str,
        id: str,
        value: str,
        tenant_id: Optional[str] = None,
        expiry_time: Optional[int] = None,
    ) -> str:
        """Set or update a cache entry by ID."""
        body: dict = {"value": value}
        if expiry_time is not None:
            body["expiryTime"] = expiry_time

        result = await http_client.put(
            f"cache/{cache_type}/id/{id}",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_cache_delete_by_id",
        description="Delete a cache entry by ID. Returns 204 on success.",
    )
    async def cdp_cache_delete_by_id(
        cache_type: str,
        id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a cache entry by ID."""
        result = await http_client.delete(
            f"cache/{cache_type}/id/{id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Cache entry '{id}' deleted from {cache_type}."

    # ═══════════════════════════════════════════════════════════════
    # BY GROUP — cache/{cacheType}/group/{group}/id/{id}
    # ═══════════════════════════════════════════════════════════════

    @server.tool(
        name="cdp_cache_get_by_group",
        description=(
            "Get a cached value by group and ID. "
            "Groups logically segregate cache keys by source or purpose."
        ),
    )
    async def cdp_cache_get_by_group(
        cache_type: str,
        group: str,
        id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a cached value by group and ID."""
        result = await http_client.get(
            f"cache/{cache_type}/group/{group}/id/{id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_cache_put_by_group",
        description="Set or update a cache entry by group and ID.",
    )
    async def cdp_cache_put_by_group(
        cache_type: str,
        group: str,
        id: str,
        value: str,
        tenant_id: Optional[str] = None,
        expiry_time: Optional[int] = None,
    ) -> str:
        """Set or update a cache entry by group and ID."""
        body: dict = {"value": value}
        if expiry_time is not None:
            body["expiryTime"] = expiry_time

        result = await http_client.put(
            f"cache/{cache_type}/group/{group}/id/{id}",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_cache_delete_by_group",
        description="Delete a cache entry by group and ID. Returns 204 on success.",
    )
    async def cdp_cache_delete_by_group(
        cache_type: str,
        group: str,
        id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a cache entry by group and ID."""
        result = await http_client.delete(
            f"cache/{cache_type}/group/{group}/id/{id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Cache entry '{group}/{id}' deleted from {cache_type}."
