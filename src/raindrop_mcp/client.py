"""
Raindrop.io API client for fetching bookmarks and collections.
"""
import os
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
