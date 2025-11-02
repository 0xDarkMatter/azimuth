"""
Quick test script to search Raindrop.io for articles.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.raindrop_mcp.client import RaindropClient


async def test_search():
    """Test searching for David Grusch articles."""
    client = RaindropClient()

    print("Searching for articles mentioning 'david grusch'...\n")

    try:
        # Search across all collections for "david grusch"
        result = await client.search_raindrops(
            collection_id=0,  # 0 = all collections
            search="david grusch",
            per_page=50  # Get up to 50 results
        )

        items = result.get("items", [])

        print(f"Found {len(items)} articles:\n")
        print("=" * 80)

        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item.get('title', 'Untitled')}")
            print(f"   URL: {item.get('link', 'N/A')}")
            print(f"   ID: {item.get('_id', 'N/A')}")

            excerpt = item.get('excerpt', '')
            if excerpt:
                short_excerpt = excerpt[:150] + "..." if len(excerpt) > 150 else excerpt
                print(f"   Description: {short_excerpt}")

            tags = item.get('tags', [])
            if tags:
                print(f"   Tags: {', '.join(tags)}")

            domain = item.get('domain', '')
            if domain:
                print(f"   Source: {domain}")

            created = item.get('created', '')
            if created:
                print(f"   Saved: {created}")

        print("\n" + "=" * 80)
        print(f"\nTotal results: {len(items)}")

    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you've set RAINDROP_TOKEN in your .env file!")
    except Exception as e:
        print(f"❌ Error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(test_search())
