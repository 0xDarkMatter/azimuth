# Azimuth Project Structure

## Current Structure (v0.1.0)

```
Azimuth/
├── src/
│   └── raindrop_mcp/           # Main package
│       ├── __init__.py         # Package exports (RaindropClient)
│       ├── client.py           # Raindrop.io API client
│       ├── server.py           # MCP server implementation
│       ├── models.py           # Pydantic models (placeholder for v0.2.0)
│       └── utils.py            # Helper functions (placeholder for v0.2.0)
│
├── cli/
│   ├── __init__.py
│   └── search.py               # CLI search tool with report generation
│
├── scripts/
│   ├── test_auth.py           # Test Raindrop.io authentication
│   ├── test_search.py         # Test search functionality
│   └── check_token.py         # Verify API token
│
├── tests/                      # Future test suite
│   └── __init__.py
│
├── docs/
│   ├── ROADMAP.md             # Project roadmap
│   └── PLAN.md                # Development plan
│
├── reports/                    # Generated search reports
│   ├── README.md
│   └── .gitkeep
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (gitignored)
├── .env.example               # Example environment file
├── .gitignore
├── README.md
└── venv/                       # Virtual environment (gitignored)
```

## Key Changes from Original Structure

### Source Code Organization
- **Before**: `raindrop_client.py`, `server.py` in root
- **After**: Organized under `src/raindrop_mcp/` package
  - Proper package structure with `__init__.py`
  - Future-ready with placeholder files for v0.2.0

### CLI Tools
- **Before**: `search_cli.py` in root
- **After**: Moved to `cli/search.py`
  - Dedicated directory for CLI tools
  - Updated reports path to `../reports/`

### Test/Utility Scripts
- **Before**: `test_auth.py`, `test_search.py`, `check_token.py` in root
- **After**: Organized under `scripts/`
  - Clear separation from source code
  - All import paths updated

### Benefits

1. **Follows Python Best Practices**
   - src layout for proper package management
   - Separation of concerns (source/CLI/scripts/tests)
   - Conventional directory names

2. **Scalable Structure**
   - Easy to add new modules in `src/raindrop_mcp/`
   - Test suite ready in `tests/`
   - CLI tools can be expanded in `cli/`

3. **Better Imports**
   - Package can be imported: `from src.raindrop_mcp import RaindropClient`
   - Internal imports use relative paths: `from .client import RaindropClient`
   - Scripts use absolute imports from `src.raindrop_mcp.client`

4. **Professional Layout**
   - Clean root directory
   - Clear purpose for each directory
   - Matches industry standards

## Import Patterns

### Within Package (src/raindrop_mcp/)
```python
from .client import RaindropClient  # Relative import
```

### From CLI/Scripts
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.raindrop_mcp.client import RaindropClient
```

### External Usage
```python
from src.raindrop_mcp import RaindropClient
```

## Updated File Paths

### Running the Server
```bash
# Old: python server.py
python src/raindrop_mcp/server.py
```

### Using the CLI
```bash
# Old: python search_cli.py "query"
python cli/search.py "query"
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "raindrop": {
      "command": "path/to/venv/Scripts/python.exe",
      "args": ["path/to/Azimuth/src/raindrop_mcp/server.py"]
    }
  }
}
```

## Version History

- **v0.1.0** (Current): MVP complete with reorganized structure
- **v0.2.0** (Next): Analytics & cleanup features
  - Will add Pydantic models to `models.py`
  - Will add utilities to `utils.py`
  - Will add test suite to `tests/`
