# Current Sprint Plan

**Sprint**: v0.1.0 MVP - Search & Retrieval
**Duration**: 1-2 days
**Goal**: Build functional MCP server with read-only Raindrop.io access for immediate value

---

## In Progress

- [-] Project setup (requirements.txt, venv, simple structure)

## Pending

- [ ] MCP SDK integration and server boilerplate
- [ ] Raindrop.io API client with authentication
- [ ] Search bookmarks tool (keyword, tag, collection filters)
- [ ] Get bookmark by ID tool (retrieve specific article)
- [ ] List collections tool (hierarchy support)
- [ ] Filter by tags tool (multi-tag queries)
- [ ] Basic error handling and logging
- [ ] README with setup and usage instructions
- [ ] Test with Claude Desktop integration

## Completed

_No completed tasks yet - fresh project start_

---

## Sprint Notes

### Current Focus

Setting up the foundation for the MCP server:
1. Simple Python script structure with requirements.txt and venv
2. MCP Python SDK integration following official patterns
3. Raindrop.io API authentication and async HTTP client setup

Once foundation is in place, implement core tools in this order:
1. **list_collections** - Understand user's organization
2. **search_bookmarks** - Primary use case (search by keyword/tag/collection)
3. **get_bookmark** - Retrieve specific article details
4. **filter_by_tags** - Tag-based discovery

### Technical Decisions

- **Runtime**: Python 3.10+ with type hints
- **MCP SDK**: mcp (official Python SDK)
- **API Client**: httpx (modern async HTTP client)
- **Data Validation**: pydantic for models and config
- **Auth**: Test token first (OAuth in v1.0.0)
- **Error Handling**: Structured exceptions with user-friendly messages
- **Logging**: Standard logging module (structured logging in v1.0.0)

### Blockers

None currently.

### Next Sprint Preview

v0.2.0 will add:
- Write operations (create, update, delete)
- Advanced search (full-text, date ranges)
- Tag management tools
- Caching for performance

---

**Checkbox Legend**:
- `[ ]` = Pending/Not started
- `[-]` = In Progress
- `[x]` = Completed

Last Updated: 2025-11-01
