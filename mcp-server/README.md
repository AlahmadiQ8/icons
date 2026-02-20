# azure-icons-mcp

MCP server for searching and fetching Microsoft Azure and Fabric SVG icons. Provides 687 icons across all major Azure service categories.

## Usage

### Claude Desktop / Cursor / VS Code

Add to your MCP config:

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

### Tools

| Tool | Description |
|------|-------------|
| `azure_icons_search` | Fuzzy search icons by keyword (e.g. "cosmos db", "key vault") |
| `azure_icons_get` | Get a specific icon by its exact ID |
| `azure_icons_list_categories` | List all categories with icon counts |
| `azure_icons_browse` | Browse icons with optional category filter and pagination |

### Example

Search for database icons:
```
azure_icons_search(query="cosmos db")
```

Returns JSON with `id`, `name`, `description`, `tags`, `filename`, and `url` for each match. Use the `url` directly as an image source in HTML or download it.
