import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
token = os.getenv('RAINDROP_TOKEN')

if token and token != 'your_test_token_here_replace_this':
    print(f"✓ Token found: {token[:20]}...")
    print(f"  Length: {len(token)} characters")
else:
    print("✗ No valid token found in .env file")
    print(f"  Current value: {token}")
