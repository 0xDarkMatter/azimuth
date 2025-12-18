# Azimuth - AI Assistant Guide

<!-- Consolidated from: WARP.md -->
<!-- Generated: 2025-01-23 -->

MCP server enabling AI assistants to access and manage Raindrop.io bookmarks through search, retrieval, and analytics tools.

## Project Structure

```
src/raindrop_mcp/     # Main package
├── __init__.py       # Package exports (RaindropClient)
├── client.py         # Raindrop.io API client
├── server.py         # MCP server implementation
├── models.py         # Reserved for Pydantic models (v0.2.0+)
└── utils.py          # Reserved for utilities (v0.2.0+)

cli/                  # CLI tools
└── search.py         # Search and analytics CLI

scripts/              # Test/utility scripts
reports/              # Generated reports (gitignored)
```

## Quick Commands

```bash
# Environment setup
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt

# Run MCP server
python src/raindrop_mcp/server.py

# CLI search
python cli/search.py "query" --format md
python cli/search.py --duplicates
python cli/search.py --check-links

# Testing
python scripts/test_auth.py
python scripts/test_search.py
python scripts/test_analytics.py
```

## Common Workflows

### Development

1. Activate venv: `.\venv\Scripts\Activate.ps1`
2. Make changes to source files
3. Test with scripts in `scripts/`
4. Test CLI with `python cli/search.py`

### Adding a New MCP Tool

1. Add method to `src/raindrop_mcp/client.py`
2. Register tool in `server.py` `list_tools` handler
3. Implement handler in `server.py` `call_tool`
4. Add test script in `scripts/`

## Conventions

- **Async:** All API calls use `httpx.AsyncClient`
- **Python:** 3.10+ required for type hints
- **Imports:** Relative within package, absolute from CLI/scripts
- **Collection IDs:** `0`=all, `-1`=unsorted, `-99`=trash
- **Rate limit:** 120 req/min, implement 6s delays between batches
- **Reports:** `reports/{query}_{timestamp}.{format}`

### Import Patterns

Within package (relative):
```python
from .client import RaindropClient
```

From CLI/scripts (absolute):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.raindrop_mcp.client import RaindropClient
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `list_collections` | Get all bookmark collections |
| `search_bookmarks` | Search with filters and pagination |
| `get_bookmark` | Retrieve single bookmark by ID |
| `list_tags` | Tag usage statistics |
| `get_statistics` | Collection analytics |
| `find_duplicates` | Detect duplicate bookmarks |
| `find_broken_links` | Check for dead links |

## Environment Setup

1. Create venv: `python -m venv venv`
2. Activate: `.\venv\Scripts\Activate.ps1`
3. Install deps: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` with your Raindrop.io token
5. Test: `python scripts/test_auth.py`

## Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "raindrop": {
      "command": "path/to/venv/python",
      "args": ["path/to/src/raindrop_mcp/server.py"],
      "env": {
        "RAINDROP_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Development Status

**Current: v0.2.0** (Analytics & Cleanup)

- v0.1.0: Complete - Core MCP server, search, CLI
- v0.2.0: In Progress - Tag management, enhanced analytics
- v0.3.0: Planned - Write operations, OAuth 2.0

See `docs/ROADMAP.md` for detailed roadmap.
