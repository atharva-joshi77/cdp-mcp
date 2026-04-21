"""
API response wrapper types.

Provides a normalized CDPResponse type that forces callers
to handle success/error cases explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

from cdp_mcp.types.cdp_types import CDPError

T = TypeVar("T")


@dataclass
class CDPSuccessResponse(Generic[T]):
    """Successful CDP API response."""

    success: bool
    data: T

    def __init__(self, data: T) -> None:
        self.success = True
        self.data = data


@dataclass
class CDPErrorResponse:
    """Failed CDP API response."""

    success: bool
    error: CDPError | str

    def __init__(self, error: CDPError | str) -> None:
        self.success = False
        self.error = error


CDPResponse = Union[CDPSuccessResponse[T], CDPErrorResponse]


def success(data: T) -> CDPSuccessResponse[T]:
    """Create a successful response."""
    return CDPSuccessResponse(data=data)


def failure(error: CDPError | str) -> CDPErrorResponse:
    """Create a failed response."""
    return CDPErrorResponse(error=error)
