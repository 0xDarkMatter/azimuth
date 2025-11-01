# Current Sprint Plan

**Sprint**: v0.2.0 - Analytics & Cleanup
**Duration**: 3-5 days
**Goal**: Add collection analytics, statistics, and maintenance tools for managing 2000+ bookmarks

---

## In Progress

_Sprint starting - ready to begin Phase 2_

## Pending

### Analytics & Statistics Tools
- [ ] Implement get_statistics MCP tool (broken links, duplicates, counts)
- [ ] Implement list_tags MCP tool (all tags with usage counts)
- [ ] Implement find_duplicates MCP tool
- [ ] Implement find_broken_links MCP tool
- [ ] Add content type breakdown to statistics
- [ ] Add untagged bookmarks finder

### Tag Management Tools
- [ ] Implement rename_tag MCP tool
- [ ] Implement merge_tags MCP tool
- [ ] Implement delete_tag MCP tool

### Enhanced CLI
- [ ] Add statistics report to CLI (--stats flag)
- [ ] Add duplicate detection to CLI
- [ ] Add broken link checker to CLI
- [ ] Add tag cleanup suggestions

### Testing & Polish
- [ ] Test with Claude Desktop integration
- [ ] Test statistics tools with large collections
- [ ] Add error handling for edge cases

## Completed

### MVP Core Features (2025-11-01)
- [x] Project setup (requirements.txt, venv, simple structure) (fb389dc)
- [x] MCP SDK integration and server boilerplate (fb389dc)
- [x] Raindrop.io API client with authentication (fb389dc)
- [x] List collections tool (hierarchy support) (fb389dc)
- [x] Search bookmarks tool (keyword, tag, collection filters) (fb389dc)
- [x] Get bookmark by ID tool (retrieve specific article) (fb389dc)
- [x] Basic error handling and logging (fb389dc)
- [x] README with setup and usage instructions (fb389dc)

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

v0.3.0 - Write Operations will add:
- Create, update, delete bookmarks
- Collection management (create, update, move)
- Highlights management
- Full-text search
- Advanced filtering

---

**Checkbox Legend**:
- `[ ]` = Pending/Not started
- `[-]` = In Progress
- `[x]` = Completed

Last Updated: 2025-11-01 (MVP Complete! 🎉)
