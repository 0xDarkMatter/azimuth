#!/usr/bin/env python3
"""
Raindrop.io MCP Server

Exposes Raindrop.io bookmarks and collections to AI assistants via MCP.
"""
import asyncio
import logging
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl
from raindrop_client import RaindropClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raindrop-mcp")

# Initialize server
server = Server("raindrop-mcp")

# Lazy initialization - only create client when needed
_raindrop_client = None

def get_raindrop_client() -> RaindropClient:
    """Get or create Raindrop client."""
    global _raindrop_client
    if _raindrop_client is None:
        _raindrop_client = RaindropClient()
    return _raindrop_client


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available Raindrop.io tools.
    """
    return [
        Tool(
            name="list_collections",
            description="List all Raindrop.io collections (both root and nested)",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_children": {
                        "type": "boolean",
                        "description": "Include nested/child collections",
                        "default": True
                    }
                },
            },
        ),
        Tool(
            name="search_bookmarks",
            description="Search Raindrop.io bookmarks with filters. Supports keyword search, tag filtering, and collection filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (supports operators like word -exclude 'exact phrase')"
                    },
                    "collection_id": {
                        "type": "integer",
                        "description": "Collection ID to search in (0=all, -1=unsorted, -99=trash)",
                        "default": 0
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (0-indexed)",
                        "default": 0
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Results per page (max 50)",
                        "default": 25
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order: -created, created, title, -title, domain, -domain",
                        "default": "-created"
                    }
                },
            },
        ),
        Tool(
            name="get_bookmark",
            description="Get a specific bookmark by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "raindrop_id": {
                        "type": "integer",
                        "description": "The raindrop (bookmark) ID"
                    }
                },
                "required": ["raindrop_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if not arguments:
        arguments = {}

    try:
        if name == "list_collections":
            include_children = arguments.get("include_children", True)

            # Get root collections
            raindrop = get_raindrop_client()
            root_response = await raindrop.list_collections()
            collections = root_response.get("items", [])

            # Get child collections if requested
            if include_children:
                child_response = await raindrop.list_child_collections()
                children = child_response.get("items", [])
                collections.extend(children)

            # Format output
            output = f"Found {len(collections)} collections:\n\n"
            for coll in collections:
                coll_id = coll.get("_id")
                title = coll.get("title", "Untitled")
                count = coll.get("count", 0)
                parent = coll.get("parent", {})
                parent_id = parent.get("$id") if parent else None

                indent = "  " if parent_id else ""
                output += f"{indent}• [{coll_id}] {title} ({count} items)"
                if parent_id:
                    output += f" [child of {parent_id}]"
                output += "\n"

            return [TextContent(type="text", text=output)]

        elif name == "search_bookmarks":
            query = arguments.get("query")
            collection_id = arguments.get("collection_id", 0)
            tags = arguments.get("tags")
            page = arguments.get("page", 0)
            per_page = arguments.get("per_page", 25)
            sort = arguments.get("sort", "-created")

            raindrop = get_raindrop_client()
            response = await raindrop.search_raindrops(
                collection_id=collection_id,
                search=query,
                tags=tags,
                page=page,
                per_page=per_page,
                sort=sort
            )

            items = response.get("items", [])
            output = f"Found {len(items)} bookmarks"
            if query:
                output += f" matching '{query}'"
            if tags:
                output += f" with tags: {', '.join(tags)}"
            output += f":\n\n"

            for item in items:
                item_id = item.get("_id")
                title = item.get("title", "Untitled")
                link = item.get("link", "")
                excerpt = item.get("excerpt", "")
                item_tags = item.get("tags", [])
                domain = item.get("domain", "")

                output += f"[{item_id}] {title}\n"
                output += f"🔗 {link}\n"
                if excerpt:
                    # Limit excerpt length
                    short_excerpt = excerpt[:200] + "..." if len(excerpt) > 200 else excerpt
                    output += f"📝 {short_excerpt}\n"
                if item_tags:
                    output += f"🏷️  {', '.join(item_tags)}\n"
                if domain:
                    output += f"🌐 {domain}\n"
                output += "\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_bookmark":
            raindrop_id = arguments.get("raindrop_id")
            if not raindrop_id:
                return [TextContent(type="text", text="Error: raindrop_id is required")]

            raindrop = get_raindrop_client()
            response = await raindrop.get_raindrop(raindrop_id)
            item = response.get("item", {})

            if not item:
                return [TextContent(type="text", text=f"Bookmark {raindrop_id} not found")]

            # Format detailed output
            output = f"Bookmark Details (ID: {raindrop_id})\n\n"
            output += f"Title: {item.get('title', 'Untitled')}\n"
            output += f"URL: {item.get('link', 'N/A')}\n"
            output += f"Type: {item.get('type', 'link')}\n"

            if item.get("excerpt"):
                output += f"\nDescription:\n{item.get('excerpt')}\n"

            if item.get("tags"):
                output += f"\nTags: {', '.join(item.get('tags', []))}\n"

            collection = item.get("collection", {})
            if collection:
                output += f"\nCollection ID: {collection.get('$id', 'N/A')}\n"

            output += f"\nDomain: {item.get('domain', 'N/A')}\n"
            output += f"Created: {item.get('created', 'N/A')}\n"
            output += f"Last Updated: {item.get('lastUpdate', 'N/A')}\n"

            if item.get("important"):
                output += f"\n⭐ Marked as important\n"

            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    logger.info("Starting Raindrop.io MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="raindrop-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
