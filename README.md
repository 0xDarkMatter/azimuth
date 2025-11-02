# Azimuth - Raindrop.io MCP Server

An MCP (Model Context Protocol) server that provides AI assistants with seamless access to your Raindrop.io article collection.

## Vision

Enable AI assistants to search, retrieve, and manage your personal knowledge base stored in Raindrop.io. This MCP server exposes your bookmarks, collections, and article content through a structured interface that LLMs can query naturally.

## Key Features

### Phase 1: Search & Retrieval (MVP - 1-2 days)
- **Search bookmarks** by keywords, tags, or collections
- **Retrieve article metadata** (title, URL, description, tags)
- **Access article content** (cached full-text when available)
- **Filter by collections** and nested collection hierarchies
- **Tag-based queries** for precise knowledge retrieval

### Phase 2: Comprehensive Feature Support
- **Collection management** (create, update, organize)
- **Bookmark CRUD** (add, update, delete bookmarks)
- **Full-text search** within article content
- **Tag operations** (create, rename, merge tags)
- **Metadata extraction** from bookmarks

## Architecture

- **Runtime**: Python 3.10+
- **Protocol**: MCP (Model Context Protocol)
- **API**: Raindrop.io REST API v1
- **Authentication**: OAuth 2.0 or Test Token

## MCP Tools Exposed

1. `search_bookmarks` - Search across all bookmarks
2. `get_bookmark` - Retrieve specific bookmark by ID
3. `list_collections` - Get user's collection hierarchy
4. `filter_by_tags` - Find bookmarks with specific tags
5. `get_article_content` - Fetch full article text (if cached)

## Target Timeline

- **MVP (v0.1.0)**: 1-2 days - Core search and retrieval
- **Feature Complete (v0.2.0)**: 1 week - Full CRUD operations
- **Production Ready (v1.0.0)**: 2+ weeks - Polish, testing, docs

## Tech Stack

- **Python 3.10+** - Modern Python with type hints
- **mcp** - Official Python MCP SDK
- **httpx** - Modern async HTTP client for Raindrop.io API
- **pydantic** - Data validation and settings management

## Getting Started

### 1. Get Your Raindrop.io API Token

1. Go to [Raindrop.io App Settings](https://app.raindrop.io/settings/integrations)
2. Click "Create new app" or select an existing app
3. Copy the **Test token** from the app settings

### 2. Setup Project

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows (PowerShell: venv\Scripts\Activate.ps1)

# Install dependencies
pip install -r requirements.txt

# Configure your API token
# Edit .env and replace the token:
RAINDROP_TOKEN=your_actual_token_here
```

### 3. Test the Server

```bash
# The MCP server runs via stdio, so it won't show output directly
# You can verify it starts without errors:
python src/raindrop_mcp/server.py
# Press Ctrl+C to stop
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP configuration (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "raindrop": {
      "command": "E:\\Projects\\Coding\\Azimuth\\venv\\Scripts\\python.exe",
      "args": ["E:\\Projects\\Coding\\Azimuth\\src\\raindrop_mcp\\server.py"],
      "env": {
        "RAINDROP_TOKEN": "your_actual_token_here"
      }
    }
  }
}
```

**Note**: Replace the paths and token with your actual values. Restart Claude Desktop after editing the config.

## Available MCP Tools

Once connected, Claude can use these tools:

1. **list_collections** - View all your Raindrop collections (with hierarchy)
2. **search_bookmarks** - Search bookmarks with filters:
   - Keyword search with operators
   - Filter by tags
   - Filter by collection
   - Pagination support
3. **get_bookmark** - Get detailed info about a specific bookmark by ID

## CLI Search Tool

For standalone searches and report generation:

```bash
# Search and generate markdown report (fetches ALL pages)
python cli/search.py "david grusch" --format md

# Search with tags
python cli/search.py "UAP" --tags aliens extraterrestrial --format json

# Search specific collection only
python cli/search.py "AI research" --collection 12345

# First page only (fast, max 50 results)
python cli/search.py "python tutorial" --first-page-only

# Adjust concurrency for faster fetching
python cli/search.py "large query" --max-concurrent 20
```

**Report Formats:**
- `txt` - Plain text, easy to read
- `md` - Markdown with clickable links
- `json` - Complete metadata for processing

Reports are saved to `reports/` directory with timestamps.

## Development Status

🚧 **In Development** - MVP phase targeting core search and retrieval functionality.

## License

ISC
