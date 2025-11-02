"""
Raindrop MCP - Model Context Protocol server for Raindrop.io

Provides AI assistants with access to Raindrop.io bookmarks and collections.
"""

from .client import RaindropClient

__version__ = "0.1.0"
__all__ = ["RaindropClient"]
