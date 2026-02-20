# Azure Icons

687 official Microsoft Azure and Fabric SVG icons for coding agents to use in architecture diagrams, documentation, and UI.

Every icon has an `id`, `name`, `description`, `tags`, and a raw GitHub `url` pointing to the SVG so agents can search and embed icons directly.

## Option 1: MCP Server

Add to your MCP config (GitHub Copilot, Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "azure-icons": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/AlahmadiQ8/icons#subdirectory=mcp-server", "azure-icons-mcp"]
    }
  }
}
```

**Tools provided:**

| Tool | Description |
|------|-------------|
| `azure_icons_search` | Fuzzy search icons by keyword (e.g. "cosmos db", "key vault") |
| `azure_icons_get` | Get a specific icon by its exact ID |
| `azure_icons_list_categories` | List all categories with icon counts |
| `azure_icons_browse` | Browse icons with optional category filter and pagination |

## Option 2: Agent Skill

Install via [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add AlahmadiQ8/icons@azure-icons
```

This gives your agent a fuzzy search script and a local icon index so it can find and fetch icons without any server running.

## Icon Source

Icons are from the official [`@fabric-msft/svg-icons`](https://www.npmjs.com/package/@fabric-msft/svg-icons) package and [Azure architecture icons](https://learn.microsoft.com/en-us/azure/architecture/icons/).

---

## Maintainer Guide

### Adding New Icons

1. Drop SVG files into `icons/` following the naming convention: `<concept>_<size>_<style>.svg`
2. Optionally add a description in `descriptions.json`
3. Rebuild: `python3 scripts/build_index.py`
4. Repackage skill: `python3 .claude/skills/skill-creator/scripts/package_skill.py skills/azure-icons ./skills`
5. Commit and push
