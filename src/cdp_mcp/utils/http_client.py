"""
Tenant-scoped HTTP client for CDP API requests.

All tool handlers use this client. It handles:
- Tenant-scoped URL construction (/v2/{tenantId}/... or bare /v2/... paths)
- Auth header injection via AuthProvider (with 401 retry & refresh)
- Query parameter serialization (URL-encoded via httpx)
- Error response normalization into CDPResponse

Path-style reference
--------------------
`path_style` controls how the base URL is assembled:

    "v2"   (default): {baseUrl}/v2/{tenantId}/{path}
                      — used by every tenant-scoped CDP service:
                        permissions, dw, cache, campaign, config, connectors,
                        reports, predictions/content, spam, status,
                        self-service provisions, etc.
    "bare":           {baseUrl}/{path}
                      — used only by endpoints that are NOT tenant-scoped:
                        /token, /authentication, /authentication/reset,
                        /sso, and /v2/config/tenants (pass `path` starting
                        with `v2/...`).
    "none":           {baseUrl}/{tenantId}/{path}   — DEPRECATED.
                      No CDP service currently exposes its controllers under
                      this layout. The historical predictions/alerts modules
                      that relied on it have been rewritten / disabled.
                      Kept only for backward compatibility; do not use in new
                      code. See MCP_AUDIT.md §4.4.
"""

from __future__ import annotations

import atexit
import logging
import time
from typing import Any, Literal, Optional
from urllib.parse import quote

import httpx

from cdp_mcp.auth.auth_provider import auth_provider
from cdp_mcp.config import get_base_url, get_default_tenant_id
from cdp_mcp.types.api_responses import CDPResponse, failure, success
from cdp_mcp.utils.error_handler import parse_error_response

logger = logging.getLogger(__name__)

PathStyle = Literal["v2", "none", "bare"]

# HTTP methods that carry a JSON body.
_BODY_METHODS = frozenset({"POST", "PUT", "PATCH"})
_DEFAULT_TIMEOUT = 30.0


class HttpClient:
    """Tenant-scoped async HTTP client for CDP API requests."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the shared httpx async client."""
        client = self._client
        if client is None or client.is_closed:
            client = httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT)
            self._client = client
        return client

    def _resolve_tenant_id(self, tenant_id: Optional[str | int] = None) -> str:
        """
        Resolve the tenant ID from the provided value or environment default.
        Raises if no tenant ID is available.
        """
        tid = str(tenant_id) if tenant_id is not None else get_default_tenant_id()
        if not tid:
            raise ValueError(
                "No tenant ID provided. Pass tenantId in the tool parameters "
                "or set CDP_TENANT_ID."
            )
        return tid

    def _build_url(
        self,
        path: str,
        tenant_id: Optional[str | int] = None,
        path_style: PathStyle = "v2",
    ) -> str:
        """
        Build the full URL for a CDP API request.

        Query parameters are *not* handled here — pass them via httpx's
        native ``params=`` kwarg so they are properly URL-encoded.
        """
        base_url = get_base_url().rstrip("/")
        clean_path = path.lstrip("/")

        if path_style == "bare":
            return f"{base_url}/{clean_path}"

        tid_quoted = quote(self._resolve_tenant_id(tenant_id), safe="")

        if path_style == "v2":
            return f"{base_url}/v2/{tid_quoted}/{clean_path}"
        # "none" — legacy / deprecated.
        return f"{base_url}/{tid_quoted}/{clean_path}"

    async def request(
        self,
        method: str,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        body: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        timeout: Optional[float] = None,
    ) -> CDPResponse:
        """
        Execute an HTTP request and return a normalized CDPResponse.

        Automatically retries once on 401 Unauthorized after forcing a
        token refresh.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: API path after the tenant segment.
            tenant_id: Tenant ID (falls back to CDP_TENANT_ID env var).
            params: Query parameters (URL-encoded by httpx).
            body: JSON body for POST/PUT/PATCH requests.
            headers: Additional headers.
            path_style: URL prefix style ("v2" default, "bare", or "none").
            timeout: Per-request timeout in seconds (overrides the 30s default).
        """
        method = method.upper()
        url = self._build_url(path, tenant_id, path_style)

        # Drop keys whose value is None so optional tool arguments don't
        # leak into the query string as "?foo=None".
        filtered_params: Optional[dict[str, Any]] = None
        if params:
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if not filtered_params:
                filtered_params = None

        send_body = body if body is not None and method in _BODY_METHODS else None

        try:
            return await self._send(
                method=method,
                url=url,
                params=filtered_params,
                body=send_body,
                extra_headers=headers,
                timeout=timeout,
                allow_reauth=True,
            )
        except httpx.HTTPError as exc:
            logger.exception("HTTP error calling %s %s", method, url)
            return failure(f"{type(exc).__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001 — last-resort guard for tool code
            logger.exception("Unexpected error calling %s %s", method, url)
            return failure(f"{type(exc).__name__}: {exc}")

    async def _send(
        self,
        *,
        method: str,
        url: str,
        params: Optional[dict[str, Any]],
        body: Optional[Any],
        extra_headers: Optional[dict[str, str]],
        timeout: Optional[float],
        allow_reauth: bool,
    ) -> CDPResponse:
        """Perform a single HTTP request (with at most one 401-driven retry)."""
        token = await auth_provider.get_token()

        request_headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra_headers:
            request_headers.update(extra_headers)

        client = await self._get_client()
        started = time.monotonic()
        response = await client.request(
            method=method,
            url=url,
            headers=request_headers,
            params=params,
            json=body,
            timeout=timeout if timeout is not None else _DEFAULT_TIMEOUT,
        )
        duration_ms = (time.monotonic() - started) * 1000.0
        logger.info(
            "CDP %s %s -> %d (%.1f ms)",
            method, url, response.status_code, duration_ms,
        )

        # One-shot recovery: if the token was rotated/revoked server-side
        # but our local cache still considers it valid, refresh and retry.
        if response.status_code == 401 and allow_reauth:
            logger.info("401 from %s %s — refreshing token and retrying once", method, url)
            auth_provider.invalidate()
            await auth_provider.get_token(force_refresh=True)
            return await self._send(
                method=method,
                url=url,
                params=params,
                body=body,
                extra_headers=extra_headers,
                timeout=timeout,
                allow_reauth=False,
            )

        if not response.is_success:
            return failure(await parse_error_response(response))

        if response.status_code == 204 or not response.content:
            return success(None)

        try:
            return success(response.json())
        except ValueError:
            # Non-JSON 2xx response — fall back to raw text so the caller
            # still sees something useful.
            return success(response.text)

    async def get(
        self,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        timeout: Optional[float] = None,
    ) -> CDPResponse:
        """Execute a GET request."""
        return await self.request(
            "GET", path,
            tenant_id=tenant_id, params=params, headers=headers,
            path_style=path_style, timeout=timeout,
        )

    async def post(
        self,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        body: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        timeout: Optional[float] = None,
    ) -> CDPResponse:
        """Execute a POST request."""
        return await self.request(
            "POST", path,
            tenant_id=tenant_id, params=params, body=body, headers=headers,
            path_style=path_style, timeout=timeout,
        )

    async def put(
        self,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        body: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        timeout: Optional[float] = None,
    ) -> CDPResponse:
        """Execute a PUT request."""
        return await self.request(
            "PUT", path,
            tenant_id=tenant_id, params=params, body=body, headers=headers,
            path_style=path_style, timeout=timeout,
        )

    async def patch(
        self,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        body: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        timeout: Optional[float] = None,
    ) -> CDPResponse:
        """Execute a PATCH request."""
        return await self.request(
            "PATCH", path,
            tenant_id=tenant_id, params=params, body=body, headers=headers,
            path_style=path_style, timeout=timeout,
        )

    async def delete(
        self,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        body: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        timeout: Optional[float] = None,
    ) -> CDPResponse:
        """Execute a DELETE request (body supported for bulk-delete actions)."""
        return await self.request(
            "DELETE", path,
            tenant_id=tenant_id, params=params, body=body, headers=headers,
            path_style=path_style, timeout=timeout,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def paginate(
        self,
        path: str,
        *,
        tenant_id: Optional[str | int] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        path_style: PathStyle = "v2",
        page_size: int = 100,
        max_pages: int = 50,
        offset_param: str = "offset",
        limit_param: str = "limit",
    ) -> CDPResponse:
        """
        Auto-paginate a GET list endpoint by walking ``offset``/``limit``.

        Stops when the server returns an empty list, fewer items than
        ``page_size``, or ``max_pages`` is reached (safety cap). Returns a
        flat list inside a CDPSuccessResponse, or the first CDPErrorResponse
        encountered.

        Most CDP list endpoints use ``offset``/``limit``; override via
        ``offset_param`` / ``limit_param`` for any that differ.
        """
        combined: list[Any] = []
        base_params = dict(params) if params else {}
        offset = int(base_params.pop(offset_param, 0) or 0)

        for _ in range(max_pages):
            page_params = {**base_params, offset_param: offset, limit_param: page_size}
            resp = await self.get(
                path,
                tenant_id=tenant_id,
                params=page_params,
                headers=headers,
                path_style=path_style,
            )
            if not resp.success:
                return resp

            data = resp.data
            page: list[Any]
            if isinstance(data, list):
                page = data
            elif isinstance(data, dict):
                # Common CDP shapes: {"items": [...]} / {"results": [...]} / {"data": [...]}
                for key in ("items", "results", "data", "content"):
                    if isinstance(data.get(key), list):
                        page = data[key]
                        break
                else:
                    # Non-list payload — return as-is.
                    return resp
            else:
                return resp

            combined.extend(page)
            if len(page) < page_size:
                break
            offset += len(page)

        return success(combined)


# Singleton instance
http_client = HttpClient()


def _shutdown() -> None:
    """Best-effort cleanup at interpreter exit.

    Runs the async `close()` on a short-lived loop if the shared httpx
    client is still open. Failures here are swallowed — we never want
    shutdown to raise.
    """
    client = http_client._client  # noqa: SLF001
    if client is None or client.is_closed:
        return
    try:
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't block a running loop from atexit; schedule close.
                loop.create_task(http_client.close())
                return
        except RuntimeError:
            pass
        asyncio.run(http_client.close())
    except Exception:  # pragma: no cover
        logger.debug("http_client shutdown best-effort close failed", exc_info=True)


atexit.register(_shutdown)
