#!/usr/bin/env python3
"""
CLI tool to search Raindrop.io and save results to reports.
"""
import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path
from raindrop_client import RaindropClient


def format_text_report(query: str, items: list, collection_id: int = 0) -> str:
    """Format search results as readable text."""
    output = f"Raindrop.io Search Report\n"
    output += f"=" * 80 + "\n\n"
    output += f"Query: '{query}'\n"
    output += f"Collection: {collection_id} (0=all, -1=unsorted, -99=trash)\n"
    output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    output += f"Results: {len(items)} bookmarks\n\n"
    output += "=" * 80 + "\n\n"

    for i, item in enumerate(items, 1):
        output += f"{i}. {item.get('title', 'Untitled')}\n"
        output += f"   URL: {item.get('link', 'N/A')}\n"
        output += f"   ID: {item.get('_id', 'N/A')}\n"

        excerpt = item.get('excerpt', '')
        if excerpt:
            short_excerpt = excerpt[:200] + "..." if len(excerpt) > 200 else excerpt
            output += f"   Description: {short_excerpt}\n"

        tags = item.get('tags', [])
        if tags:
            output += f"   Tags: {', '.join(tags)}\n"

        domain = item.get('domain', '')
        if domain:
            output += f"   Source: {domain}\n"

        created = item.get('created', '')
        if created:
            output += f"   Saved: {created}\n"

        output += "\n"

    output += "=" * 80 + "\n"
    output += f"End of Report - {len(items)} results\n"

    return output


def save_report(query: str, items: list, format: str = "txt", collection_id: int = 0):
    """Save search results to reports directory."""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Create safe filename from query
    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_query = safe_query.replace(' ', '_')[:50]  # Limit length

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{safe_query}_{timestamp}"

    if format == "txt":
        filepath = reports_dir / f"{filename}.txt"
        content = format_text_report(query, items, collection_id)
        filepath.write_text(content, encoding='utf-8')
    elif format == "json":
        filepath = reports_dir / f"{filename}.json"
        report_data = {
            "query": query,
            "collection_id": collection_id,
            "generated": datetime.now().isoformat(),
            "count": len(items),
            "results": items
        }
        filepath.write_text(json.dumps(report_data, indent=2), encoding='utf-8')
    elif format == "md":
        filepath = reports_dir / f"{filename}.md"
        content = format_markdown_report(query, items, collection_id)
        filepath.write_text(content, encoding='utf-8')

    return filepath


def format_markdown_report(query: str, items: list, collection_id: int = 0) -> str:
    """Format search results as markdown."""
    output = f"# Raindrop.io Search Report\n\n"
    output += f"**Query:** `{query}`  \n"
    output += f"**Collection:** {collection_id} (0=all, -1=unsorted, -99=trash)  \n"
    output += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    output += f"**Results:** {len(items)} bookmarks\n\n"
    output += "---\n\n"

    for i, item in enumerate(items, 1):
        title = item.get('title', 'Untitled')
        link = item.get('link', '#')
        item_id = item.get('_id', 'N/A')

        output += f"## {i}. [{title}]({link})\n\n"
        output += f"**ID:** {item_id}  \n"

        excerpt = item.get('excerpt', '')
        if excerpt:
            output += f"\n{excerpt}\n\n"

        tags = item.get('tags', [])
        if tags:
            tag_badges = " ".join(f"`{tag}`" for tag in tags)
            output += f"**Tags:** {tag_badges}  \n"

        domain = item.get('domain', '')
        if domain:
            output += f"**Source:** {domain}  \n"

        created = item.get('created', '')
        if created:
            output += f"**Saved:** {created}  \n"

        output += "\n---\n\n"

    output += f"\n**Total Results:** {len(items)}\n"

    return output


async def fetch_all_pages(
    client: RaindropClient,
    query: str,
    collection_id: int = 0,
    tags: list = None,
    per_page: int = 50,
    max_concurrent: int = 10
):
    """Fetch all pages of results with concurrent requests."""
    # First, get the first page to determine total count
    print("Fetching first page to determine total count...")
    first_result = await client.search_raindrops(
        collection_id=collection_id,
        search=query,
        tags=tags,
        page=0,
        per_page=per_page
    )

    all_items = first_result.get("items", [])
    first_page_count = len(all_items)

    print(f"First page: {first_page_count} results")

    # If we got less than per_page, we have all results
    if first_page_count < per_page:
        print(f"[OK] All results retrieved ({first_page_count} total)")
        return all_items

    # Otherwise, fetch remaining pages
    # Estimate total pages (Raindrop API doesn't return total count)
    # We'll keep fetching until we get an empty page
    print(f"Fetching additional pages (batches of {max_concurrent})...")

    page = 1
    while True:
        # Create batch of page requests
        batch_pages = list(range(page, page + max_concurrent))

        # Fetch batch concurrently
        tasks = [
            client.search_raindrops(
                collection_id=collection_id,
                search=query,
                tags=tags,
                page=p,
                per_page=per_page
            )
            for p in batch_pages
        ]

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        empty_count = 0
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"  Warning: Page fetch error: {result}")
                empty_count += 1
                continue

            items = result.get("items", [])
            if not items:
                empty_count += 1
            else:
                all_items.extend(items)

        print(f"  Pages {page}-{page + max_concurrent - 1}: +{len(all_items) - first_page_count} new items (total: {len(all_items)})")

        # If all pages in this batch were empty, we're done
        if empty_count == len(batch_results):
            break

        page += max_concurrent

        # Safety limit to prevent infinite loops
        if page > 100:  # Max 100 * max_concurrent pages
            print(f"  Warning: Reached safety limit at page {page}")
            break

    print(f"\n[OK] Retrieved all results: {len(all_items)} total bookmarks")
    return all_items


async def search_and_save(
    query: str,
    collection_id: int = 0,
    tags: list = None,
    format: str = "txt",
    fetch_all: bool = True,
    max_concurrent: int = 10
):
    """Search Raindrop and save results."""
    client = RaindropClient()

    print(f"Searching for: '{query}'")
    if tags:
        print(f"With tags: {', '.join(tags)}")
    print(f"Collection: {collection_id}")
    print(f"Fetch all: {fetch_all}")
    print()

    try:
        if fetch_all:
            items = await fetch_all_pages(
                client,
                query,
                collection_id,
                tags,
                per_page=50,  # Max allowed by API
                max_concurrent=max_concurrent
            )
        else:
            # Single page fetch
            result = await client.search_raindrops(
                collection_id=collection_id,
                search=query,
                tags=tags,
                page=0,
                per_page=50
            )
            items = result.get("items", [])
            print(f"Found {len(items)} results (first page only)\n")

        if not items:
            print("No results found.")
            return None

        # Save report
        print()
        filepath = save_report(query, items, format, collection_id)
        print(f"[OK] Report saved to: {filepath}")
        print(f"  Format: {format}")
        print(f"  Size: {filepath.stat().st_size:,} bytes")
        print(f"  Results: {len(items)} bookmarks")

        return items

    except ValueError as e:
        print(f"Error: {e}")
        print("\nMake sure RAINDROP_TOKEN is set in your .env file!")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Raindrop.io and save results to reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_cli.py "david grusch"
  python search_cli.py "UAP" --tags aliens --format md
  python search_cli.py "AI" --collection 12345 --format json
  python search_cli.py "python tutorial" --per-page 100
        """
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "-c", "--collection",
        type=int,
        default=0,
        help="Collection ID (0=all, -1=unsorted, -99=trash)"
    )
    parser.add_argument(
        "-t", "--tags",
        nargs="+",
        help="Filter by tags"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "json", "md"],
        default="txt",
        help="Output format (default: txt)"
    )
    parser.add_argument(
        "--first-page-only",
        action="store_true",
        help="Fetch only the first page (default: fetch all pages)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Max concurrent page requests (default: 10)"
    )

    args = parser.parse_args()

    asyncio.run(search_and_save(
        query=args.query,
        collection_id=args.collection,
        tags=args.tags,
        format=args.format,
        fetch_all=not args.first_page_only,
        max_concurrent=args.max_concurrent
    ))


if __name__ == "__main__":
    main()
