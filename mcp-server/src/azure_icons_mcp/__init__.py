"""Azure Icons MCP Server - Search and fetch Microsoft Azure and Fabric SVG icons."""

from azure_icons_mcp.server import mcp


def main():
    mcp.run()


__all__ = ["main", "mcp"]
