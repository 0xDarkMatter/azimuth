"""
Test the analytics tools.
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.raindrop_mcp.client import RaindropClient


async def test_analytics():
    """Test all analytics features."""
    client = RaindropClient()

    print("=" * 60)
    print("Testing Analytics Tools")
    print("=" * 60)

    # Test 1: List Tags
    print("\n1. Testing list_tags...")
    tags_response = await client.get_tags(0)
    tags = tags_response.get("items", [])
    print(f"[OK] Found {len(tags)} tags")
    if tags:
        top_5 = sorted(tags, key=lambda t: t.get("count", 0), reverse=True)[:5]
        print("   Top 5 tags:")
        for tag in top_5:
            print(f"   - #{tag.get('_id')}: {tag.get('count')} bookmarks")

    # Test 2: Get Statistics (without link checking)
    print("\n2. Testing get_statistics (without link check)...")
    items = await client.get_all_raindrops(0)
    total = len(items)
    print(f"[OK] Fetched all {total} bookmarks")

    # Count duplicates
    url_map = {}
    for item in items:
        url = item.get("link", "")
        if url:
            url_map[url] = url_map.get(url, 0) + 1

    duplicates = sum(1 for count in url_map.values() if count > 1)
    print(f"[OK] Found {duplicates} duplicate URLs")

    # Count untagged
    untagged = sum(1 for item in items if not item.get("tags", []))
    print(f"[OK] Found {untagged} untagged bookmarks ({untagged * 100 // total if total > 0 else 0}%)")

    # Content types
    type_counts = {}
    for item in items:
        item_type = item.get("type", "link")
        type_counts[item_type] = type_counts.get(item_type, 0) + 1

    print("[OK] Content type breakdown:")
    for item_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {item_type}: {count} ({count * 100 // total}%)")

    # Test 3: Find Duplicates
    print("\n3. Testing find_duplicates...")
    url_groups = {}
    for item in items:
        url = item.get("link", "")
        if url:
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(item)

    duplicate_urls = {url: bookmarks for url, bookmarks in url_groups.items() if len(bookmarks) > 1}
    if duplicate_urls:
        print(f"[OK] Found {len(duplicate_urls)} URLs with duplicates")
        # Show first duplicate
        first_url, first_group = next(iter(sorted(duplicate_urls.items(), key=lambda x: len(x[1]), reverse=True)))
        print(f"   Example: {first_url}")
        print(f"   - {len(first_group)} copies")
    else:
        print("[OK] No duplicates found")

    # Test 4: Broken Links (check first 10 only for speed)
    print("\n4. Testing find_broken_links (checking first 10 only)...")
    from src.raindrop_mcp.server import check_links_status
    sample_items = items[:10]
    broken = await check_links_status(sample_items, timeout=5)
    print(f"[OK] Checked {len(sample_items)} links, found {len(broken)} broken")
    if broken:
        for item, status in broken[:3]:
            print(f"   - {item.get('title', 'Untitled')}: {status}")

    print("\n" + "=" * 60)
    print("All analytics tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_analytics())
