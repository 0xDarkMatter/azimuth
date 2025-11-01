# Azimuth - Raindrop.io MCP Server Roadmap

## Vision

Enable AI assistants to seamlessly access and manage your personal knowledge base stored in Raindrop.io. This MCP server provides Claude and other LLMs with structured tools to search, retrieve, and interact with your curated article collection, making your bookmarked content instantly available as context for AI conversations.

## Current Phase: v0.2.0 - Analytics & Cleanup

Focus on collection health, statistics, and maintenance tools to help manage 2000+ bookmarks effectively.

## Version Roadmap

### v0.1.0 - MVP (Search & Retrieval) ✅
**Status**: Complete (Pending testing)
**Timeline**: 1-2 days
**Goal**: Functional MCP server with read-only Raindrop.io access

- [x] Project setup (requirements.txt, venv, simple structure)
- [x] MCP SDK integration and server boilerplate
- [x] Raindrop.io API client with authentication
- [x] Search bookmarks tool (keyword, tag, collection filters)
- [x] Get bookmark by ID tool (retrieve specific article)
- [x] List collections tool (hierarchy support)
- [-] Filter by tags tool (multi-tag queries) [implemented via search_bookmarks]
- [x] Basic error handling and logging
- [x] README with setup and usage instructions
- [ ] Test with Claude Desktop integration

### v0.2.0 - Analytics & Cleanup 🔍
**Status**: Planned (Next Phase)
**Timeline**: 3-5 days
**Goal**: Collection health, analytics, and maintenance tools

**Priority 1: Analytics & Statistics**
- [ ] Get collection statistics tool (broken links, duplicates, tag counts)
- [ ] List all tags with usage counts tool
- [ ] Find duplicate bookmarks tool
- [ ] Find broken links tool
- [ ] Get content type breakdown (articles, images, videos)
- [ ] Untagged bookmarks finder
- [ ] Favorite/important bookmarks counter

**Priority 2: Tag Management**
- [ ] Rename tag tool
- [ ] Merge tags tool
- [ ] Delete unused tags tool
- [ ] Tag suggestions based on content

**Priority 3: Enhanced CLI**
- [ ] Statistics report generation
- [ ] Duplicate detection report
- [ ] Broken link checker report
- [ ] Tag cleanup suggestions

### v0.3.0 - Write Operations 📝
**Status**: Planned
**Timeline**: 1 week
**Goal**: Full CRUD operations for bookmarks and collections

**Bookmark Operations**
- [ ] Create bookmark tool (save new articles with auto-metadata)
- [ ] Update bookmark tool (edit metadata, tags, description)
- [ ] Delete bookmark tool (move to trash/permanent delete)
- [ ] Bulk bookmark operations (tag multiple, move to collection)
- [ ] Set importance/favorite flag
- [ ] Add/edit notes

**Collection Operations**
- [ ] Create collection tool (new collections)
- [ ] Update collection tool (rename, reorganize, change parent)
- [ ] Delete collection tool
- [ ] Move collections in hierarchy
- [ ] Set collection view mode (list/grid/masonry)
- [ ] Set collection privacy

**Advanced Features**
- [ ] Highlights management (create, edit, delete)
- [ ] Full-text search within article content
- [ ] Advanced filtering (date ranges, favorites)
- [ ] Caching layer for performance
- [ ] Comprehensive unit tests
- [ ] Integration tests with mock API

### v1.0.0 - Production Ready 🚀
**Status**: Planned
**Timeline**: 2+ weeks
**Goal**: Battle-tested, documented, production-grade server

- [ ] OAuth 2.0 flow (not just test tokens)
- [ ] Rate limiting and retry logic
- [ ] Advanced caching strategies
- [ ] Webhook support (real-time updates)
- [ ] Batch operations optimization
- [ ] Export tools (markdown, JSON, CSV formats)
- [ ] Analytics tools (reading stats, collection insights)
- [ ] Comprehensive error handling
- [ ] Security audit and best practices
- [ ] Performance benchmarks
- [ ] Complete API documentation
- [ ] Video tutorial and examples
- [ ] npm package publication

### Future Enhancements

- [ ] AI-powered bookmark categorization
- [ ] Automatic tag suggestions based on content
- [ ] Duplicate detection and merging
- [ ] Integration with other read-later services
- [ ] Browser extension for quick saves
- [ ] Shared collection support
- [ ] Custom metadata fields
- [ ] Advanced analytics dashboard
- [ ] Backup and restore functionality

---

**Checkbox Legend**:
- `[ ]` = Pending/Not started
- `[-]` = In Progress
- `[x]` = Completed

Last Updated: 2025-11-01
