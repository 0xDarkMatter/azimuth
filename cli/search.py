#!/usr/bin/env python3
"""
CLI tool to search Raindrop.io and save results to reports.
"""
import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.raindrop_mcp.client import RaindropClient
from src.raindrop_mcp.server import check_links_status


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
    # Reports directory is at project root
    reports_dir = Path(__file__).parent.parent / "reports"
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


async def find_duplicates_report(collection_id: int = 0, format: str = "txt"):
    """Find and report duplicate bookmarks."""
    client = RaindropClient()

    print(f"Finding duplicate URLs in collection {collection_id}...")
    print("This may take a while with large collections...")
    print()

    try:
        # Fetch all bookmarks using the rate-limited method
        items = await client.get_all_raindrops(collection_id=collection_id)
        print(f"[OK] Fetched {len(items)} bookmarks")

        # Group by URL
        url_groups = {}
        for item in items:
            url = item.get("link", "")
            if url:
                if url not in url_groups:
                    url_groups[url] = []
                url_groups[url].append(item)

        # Find duplicates
        duplicates = {url: bookmarks for url, bookmarks in url_groups.items() if len(bookmarks) > 1}

        if not duplicates:
            print("\n[OK] No duplicate bookmarks found!")
            return None

        total_redundant = sum(len(bookmarks) - 1 for bookmarks in duplicates.values())
        print(f"\n[FOUND] {len(duplicates)} URLs with duplicates ({total_redundant} redundant bookmarks)")
        print()

        # Format report
        output = f"Duplicate Bookmarks Report\n"
        output += f"=" * 80 + "\n\n"
        output += f"Collection: {collection_id} (0=all, -1=unsorted, -99=trash)\n"
        output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += f"Total Bookmarks Scanned: {len(items)}\n"
        output += f"Duplicate URLs: {len(duplicates)}\n"
        output += f"Redundant Bookmarks: {total_redundant}\n\n"
        output += "=" * 80 + "\n\n"

        # Sort by number of duplicates (most duplicates first)
        for url, bookmarks in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True):
            output += f"URL: {url}\n"
            output += f"Copies: {len(bookmarks)}\n\n"

            for i, bookmark in enumerate(bookmarks, 1):
                item_id = bookmark.get("_id")
                title = bookmark.get("title", "Untitled")
                created = bookmark.get("created", "")[:10]
                tags = bookmark.get("tags", [])

                output += f"  {i}. [{item_id}] {title}\n"
                if created:
                    output += f"     Created: {created}\n"
                if tags:
                    output += f"     Tags: {', '.join(tags[:5])}\n"
                output += "\n"

            output += "-" * 80 + "\n\n"

        # Save report
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"duplicates_{timestamp}.txt"
        filepath = reports_dir / filename
        filepath.write_text(output, encoding='utf-8')

        print(f"[OK] Duplicate report saved to: {filepath}")
        print(f"  Total URLs with duplicates: {len(duplicates)}")
        print(f"  Redundant bookmarks: {total_redundant}")

        return duplicates

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


async def check_broken_links_report(collection_id: int = 0, timeout: int = 10, format: str = "txt"):
    """Check bookmarks for broken links and generate report."""
    client = RaindropClient()

    print(f"Checking links in collection {collection_id}...")
    print(f"Timeout: {timeout} seconds per request")
    print("This may take a while with large collections...")
    print()

    try:
        # Fetch all bookmarks
        items = await client.get_all_raindrops(collection_id=collection_id)
        print(f"[OK] Fetched {len(items)} bookmarks")
        print(f"[CHECKING] Testing {len(items)} URLs (this will take several minutes)...")
        print()

        # Check links with progress updates
        broken = await check_links_status(items, timeout=timeout)

        print(f"\n[DONE] Checked {len(items)} links")
        print(f"[FOUND] {len(broken)} broken/unreachable links ({len(broken) * 100 // len(items) if len(items) > 0 else 0}%)")
        print()

        if not broken:
            print("[OK] No broken links found!")
            return None

        # Format report
        output = f"Broken Links Report\n"
        output += f"=" * 80 + "\n\n"
        output += f"Collection: {collection_id} (0=all, -1=unsorted, -99=trash)\n"
        output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += f"Total Bookmarks Checked: {len(items)}\n"
        output += f"Broken Links: {len(broken)}\n"
        output += f"Success Rate: {(len(items) - len(broken)) * 100 // len(items) if len(items) > 0 else 0}%\n\n"
        output += "=" * 80 + "\n\n"

        for i, (item, status) in enumerate(broken, 1):
            item_id = item.get("_id")
            title = item.get("title", "Untitled")
            link = item.get("link", "")
            tags = item.get("tags", [])

            output += f"{i}. [{item_id}] {title}\n"
            output += f"   URL: {link}\n"
            output += f"   Status: {status}\n"
            if tags:
                output += f"   Tags: {', '.join(tags[:5])}\n"
            output += "\n"

        # Save report
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"broken_links_{timestamp}.txt"
        filepath = reports_dir / filename
        filepath.write_text(output, encoding='utf-8')

        print(f"[OK] Broken links report saved to: {filepath}")
        print(f"  Broken links: {len(broken)}")
        print(f"  Success rate: {(len(items) - len(broken)) * 100 // len(items)}%")

        return broken

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


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
        description="Search Raindrop.io and save results to reports, or run analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search
  python cli/search.py "david grusch"
  python cli/search.py "UAP" --tags aliens --format md
  python cli/search.py "AI" --collection 12345 --format json

  # Analytics
  python cli/search.py --duplicates
  python cli/search.py --duplicates --collection 12345
  python cli/search.py --check-links --timeout 5
        """
    )

    # Analytics modes (mutually exclusive with search)
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Find duplicate bookmarks (same URL)"
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Check for broken/unreachable links"
    )

    # Search query (optional if using analytics mode)
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (not used in analytics modes)"
    )

    # Common arguments
    parser.add_argument(
        "-c", "--collection",
        type=int,
        default=0,
        help="Collection ID (0=all, -1=unsorted, -99=trash)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "json", "md"],
        default="txt",
        help="Output format (default: txt)"
    )

    # Search-specific arguments
    parser.add_argument(
        "-t", "--tags",
        nargs="+",
        help="Filter by tags (search mode only)"
    )
    parser.add_argument(
        "--first-page-only",
        action="store_true",
        help="Fetch only the first page (search mode only)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Max concurrent page requests (default: 10)"
    )

    # Link checking specific
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds for link checking (default: 10)"
    )

    args = parser.parse_args()

    # Determine mode
    if args.duplicates:
        # Duplicate detection mode
        asyncio.run(find_duplicates_report(
            collection_id=args.collection,
            format=args.format
        ))
    elif args.check_links:
        # Broken link checking mode
        asyncio.run(check_broken_links_report(
            collection_id=args.collection,
            timeout=args.timeout,
            format=args.format
        ))
    else:
        # Search mode (default)
        if not args.query:
            parser.error("query is required for search mode (or use --duplicates / --check-links)")

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
