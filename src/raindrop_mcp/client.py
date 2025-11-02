"""
Raindrop.io API client for fetching bookmarks and collections.
"""
import os
import asyncio
import httpx
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class RaindropClient:
    """Client for interacting with Raindrop.io API."""

    BASE_URL = "https://api.raindrop.io/rest/v1"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Raindrop client.

        Args:
            token: Raindrop.io API test token. If not provided, reads from RAINDROP_TOKEN env var.
        """
        self.token = token or os.getenv("RAINDROP_TOKEN")
        if not self.token:
            raise ValueError("RAINDROP_TOKEN must be provided or set in environment")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def list_collections(self) -> Dict[str, Any]:
        """
        Get all root collections.

        Returns:
            Dict with 'result' and 'items' (list of collections)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/collections",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def list_child_collections(self) -> Dict[str, Any]:
        """
        Get all nested/child collections.

        Returns:
            Dict with 'result' and 'items' (list of nested collections)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/collections/childrens",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def search_raindrops(
        self,
        collection_id: int = 0,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 0,
        per_page: int = 25,
        sort: str = "-created"
    ) -> Dict[str, Any]:
        """
        Search/list raindrops (bookmarks).

        Args:
            collection_id: Collection ID (0=all, -1=unsorted, -99=trash)
            search: Search query with operators
            tags: List of tags to filter by
            page: Page number (0-indexed)
            per_page: Results per page (max 50)
            sort: Sort order (-created, title, domain, etc.)

        Returns:
            Dict with 'result' and 'items' (list of raindrops)
        """
        params = {
            "page": page,
            "perpage": min(per_page, 50),
            "sort": sort
        }

        # Build search query with tags if provided
        if search or tags:
            query_parts = []
            if search:
                query_parts.append(search)
            if tags:
                # Tag search format: #tag1 #tag2
                tag_query = " ".join(f"#{tag}" for tag in tags)
                query_parts.append(tag_query)
            params["search"] = " ".join(query_parts)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/raindrops/{collection_id}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_raindrop(self, raindrop_id: int) -> Dict[str, Any]:
        """
        Get a single raindrop by ID.

        Args:
            raindrop_id: The raindrop ID

        Returns:
            Dict with 'result' and 'item' (single raindrop object)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/raindrop/{raindrop_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_tags(self, collection_id: int = 0) -> Dict[str, Any]:
        """
        Get all tags with usage counts.

        Args:
            collection_id: Collection ID (0=all collections)

        Returns:
            Dict with 'result' and 'items' (list of tags with counts)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/tags/{collection_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_all_raindrops(
        self,
        collection_id: int = 0,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_concurrent: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch ALL raindrops with pagination (batched concurrent requests).

        Args:
            collection_id: Collection ID (0=all, -1=unsorted, -99=trash)
            search: Optional search query
            tags: Optional list of tags to filter by
            max_concurrent: Maximum concurrent page requests

        Returns:
            List of all raindrop items
        """
        # First request to get total count
        first_page = await self.search_raindrops(
            collection_id=collection_id,
            search=search,
            tags=tags,
            page=0,
            per_page=50
        )

        items = first_page.get("items", [])
        count = first_page.get("count", 0)

        # If we got everything in first page, return early
        if count <= 50:
            return items

        # Calculate remaining pages
        total_pages = (count + 49) // 50  # Round up
        remaining_pages = list(range(1, total_pages))

        # Fetch remaining pages in batches with rate limiting
        # API limit: 120 req/min = 2 req/sec
        # With max_concurrent=10, we need ~5 sec between batches
        async with httpx.AsyncClient() as client:
            for i in range(0, len(remaining_pages), max_concurrent):
                batch = remaining_pages[i:i + max_concurrent]
                tasks = []

                for page in batch:
                    task = self.search_raindrops(
                        collection_id=collection_id,
                        search=search,
                        tags=tags,
                        page=page,
                        per_page=50
                    )
                    tasks.append(task)

                # Wait for batch to complete
                results = await asyncio.gather(*tasks)
                for result in results:
                    items.extend(result.get("items", []))

                # Rate limiting: sleep 6 seconds between batches (120 req/min limit)
                if i + max_concurrent < len(remaining_pages):
                    await asyncio.sleep(6)

        return items
