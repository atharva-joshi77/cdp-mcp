"""
Entry point for the CDP MCP Server.

Starts the server using stdio transport for CLI integration.
Usage: python -m cdp_mcp
"""

from cdp_mcp.server import mcp


def main() -> None:
    """Run the CDP MCP Server on stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
