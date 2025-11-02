"""Test Raindrop.io authentication."""
import asyncio
import httpx
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


async def test_auth():
    """Test if the token works with Raindrop API."""
    token = os.getenv("RAINDROP_TOKEN")

    print(f"Testing authentication with token: {token[:20]}...")
    print()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Try to get user info (simple authenticated endpoint)
    async with httpx.AsyncClient() as client:
        try:
            print("Testing GET /rest/v1/user endpoint...")
            response = await client.get(
                "https://api.raindrop.io/rest/v1/user",
                headers=headers,
                timeout=10.0
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}")

            if response.status_code == 200:
                print("\nSUCCESS! Token is valid.")
                user_data = response.json()
                print(f"Authenticated as: {user_data.get('user', {}).get('email', 'N/A')}")
            else:
                print("\nFAILED! Token authentication failed.")
                print("Please check:")
                print("1. Is this a Test Token from https://app.raindrop.io/settings/integrations?")
                print("2. Did you create an app first?")
                print("3. Is the token copied correctly?")

        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(test_auth())
