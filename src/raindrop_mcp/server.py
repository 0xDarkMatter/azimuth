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
from .client import RaindropClient

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
        Tool(
            name="list_tags",
            description="List all tags with usage counts",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "integer",
                        "description": "Collection ID (0=all collections)",
                        "default": 0
                    },
                    "min_count": {
                        "type": "integer",
                        "description": "Only show tags with at least this many bookmarks",
                        "default": 1
                    }
                },
            },
        ),
        Tool(
            name="get_statistics",
            description="Get collection statistics including total count, duplicates, broken links, untagged bookmarks, and content type breakdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "integer",
                        "description": "Collection ID to analyze (0=all, -1=unsorted)",
                        "default": 0
                    },
                    "check_links": {
                        "type": "boolean",
                        "description": "Check for broken links (may be slow for large collections)",
                        "default": False
                    }
                },
            },
        ),
        Tool(
            name="find_duplicates",
            description="Find duplicate bookmarks (same URL)",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "integer",
                        "description": "Collection ID to search (0=all)",
                        "default": 0
                    }
                },
            },
        ),
        Tool(
            name="find_broken_links",
            description="Check bookmarks for broken/unreachable links",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "integer",
                        "description": "Collection ID to check (0=all)",
                        "default": 0
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "default": 10
                    }
                },
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

        elif name == "list_tags":
            collection_id = arguments.get("collection_id", 0)
            min_count = arguments.get("min_count", 1)

            raindrop = get_raindrop_client()
            response = await raindrop.get_tags(collection_id)
            tags = response.get("items", [])

            # Filter by min_count
            filtered_tags = [t for t in tags if t.get("count", 0) >= min_count]

            # Sort by count (descending)
            filtered_tags.sort(key=lambda t: t.get("count", 0), reverse=True)

            output = f"Found {len(filtered_tags)} tags"
            if min_count > 1:
                output += f" (with {min_count}+ bookmarks)"
            output += ":\n\n"

            for tag in filtered_tags:
                tag_name = tag.get("_id", "")
                count = tag.get("count", 0)
                output += f"#{tag_name} ({count})\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_statistics":
            collection_id = arguments.get("collection_id", 0)
            check_links = arguments.get("check_links", False)

            raindrop = get_raindrop_client()
            logger.info(f"Fetching all bookmarks from collection {collection_id}...")
            items = await raindrop.get_all_raindrops(collection_id=collection_id)

            total_count = len(items)

            # Find duplicates (same URL)
            url_map = {}
            for item in items:
                url = item.get("link", "")
                if url:
                    if url not in url_map:
                        url_map[url] = []
                    url_map[url].append(item)

            duplicates = {url: bookmarks for url, bookmarks in url_map.items() if len(bookmarks) > 1}
            duplicate_count = sum(len(bookmarks) - 1 for bookmarks in duplicates.values())

            # Count untagged
            untagged = [item for item in items if not item.get("tags", [])]
            untagged_count = len(untagged)

            # Content type breakdown
            type_counts = {}
            for item in items:
                item_type = item.get("type", "link")
                type_counts[item_type] = type_counts.get(item_type, 0) + 1

            # Check broken links if requested
            broken_count = 0
            if check_links:
                logger.info("Checking links (this may take a while)...")
                broken_count = await check_broken_links(items)

            # Format output
            output = f"📊 Collection Statistics\n\n"
            output += f"Total Bookmarks: {total_count}\n"
            output += f"Duplicates: {duplicate_count} redundant bookmarks\n"
            output += f"Untagged: {untagged_count} ({untagged_count * 100 // total_count if total_count > 0 else 0}%)\n"

            if check_links:
                output += f"Broken Links: {broken_count} ({broken_count * 100 // total_count if total_count > 0 else 0}%)\n"

            output += f"\n📑 Content Types:\n"
            for content_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                output += f"  {content_type}: {count} ({count * 100 // total_count}%)\n"

            return [TextContent(type="text", text=output)]

        elif name == "find_duplicates":
            collection_id = arguments.get("collection_id", 0)

            raindrop = get_raindrop_client()
            logger.info(f"Fetching all bookmarks from collection {collection_id}...")
            items = await raindrop.get_all_raindrops(collection_id=collection_id)

            # Group by URL
            url_map = {}
            for item in items:
                url = item.get("link", "")
                if url:
                    if url not in url_map:
                        url_map[url] = []
                    url_map[url].append(item)

            # Find duplicates
            duplicates = {url: bookmarks for url, bookmarks in url_map.items() if len(bookmarks) > 1}

            if not duplicates:
                return [TextContent(type="text", text="No duplicate bookmarks found!")]

            total_duplicates = sum(len(bookmarks) - 1 for bookmarks in duplicates.values())
            output = f"Found {len(duplicates)} URLs with duplicates ({total_duplicates} redundant bookmarks):\n\n"

            for url, bookmarks in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True):
                output += f"🔗 {url}\n"
                output += f"   {len(bookmarks)} copies:\n"
                for bookmark in bookmarks:
                    item_id = bookmark.get("_id")
                    title = bookmark.get("title", "Untitled")
                    created = bookmark.get("created", "")[:10]  # Date only
                    tags = bookmark.get("tags", [])
                    output += f"   • [{item_id}] {title}"
                    if created:
                        output += f" (created {created})"
                    if tags:
                        output += f" [tags: {', '.join(tags[:3])}]"
                    output += "\n"
                output += "\n"

            return [TextContent(type="text", text=output)]

        elif name == "find_broken_links":
            collection_id = arguments.get("collection_id", 0)
            timeout = arguments.get("timeout", 10)

            raindrop = get_raindrop_client()
            logger.info(f"Fetching all bookmarks from collection {collection_id}...")
            items = await raindrop.get_all_raindrops(collection_id=collection_id)

            logger.info(f"Checking {len(items)} links (timeout={timeout}s)...")
            broken = await check_links_status(items, timeout)

            if not broken:
                return [TextContent(type="text", text="No broken links found!")]

            output = f"Found {len(broken)} broken/unreachable links:\n\n"
            for item, status in broken:
                item_id = item.get("_id")
                title = item.get("title", "Untitled")
                link = item.get("link", "")
                output += f"[{item_id}] {title}\n"
                output += f"🔗 {link}\n"
                output += f"❌ Status: {status}\n\n"

            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def check_link_status(url: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Check if a URL is accessible.

    Returns:
        Tuple of (is_ok, status_message)
    """
    import httpx

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.head(url, timeout=timeout)
            if response.status_code < 400:
                return (True, f"{response.status_code}")
            else:
                return (False, f"HTTP {response.status_code}")
    except httpx.TimeoutException:
        return (False, "Timeout")
    except httpx.ConnectError:
        return (False, "Connection failed")
    except Exception as e:
        return (False, f"Error: {str(e)[:50]}")


async def check_links_status(items: list, timeout: int = 10, max_concurrent: int = 20) -> list:
    """
    Check multiple URLs for broken links.

    Returns:
        List of (item, status) tuples for broken links
    """
    broken = []

    # Process in batches to avoid overwhelming the system
    for i in range(0, len(items), max_concurrent):
        batch = items[i:i + max_concurrent]
        tasks = []

        for item in batch:
            url = item.get("link", "")
            if url:
                tasks.append((item, check_link_status(url, timeout)))

        # Wait for batch
        results = await asyncio.gather(*[task[1] for task in tasks])

        for (item, _), (is_ok, status) in zip(tasks, results):
            if not is_ok:
                broken.append((item, status))

    return broken


async def check_broken_links(items: list) -> int:
    """
    Count broken links in a list of items.

    Returns:
        Number of broken links
    """
    broken = await check_links_status(items)
    return len(broken)


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
