# Microsoft Fabric Icons

A structured icon repository for **coding agents** to easily discover and use official [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/) icons in diagrams, documentation, and UI.

## Quick Start (for Agents)

Fetch the icon index:

```
https://raw.githubusercontent.com/AlahmadiQ8/icons/main/index.json
```

The index contains 373 icons, each with:

| Field | Description |
|-------|-------------|
| `id` | Machine-friendly identifier (snake_case) |
| `name` | Human-readable display name |
| `description` | What the icon represents |
| `tags` | Searchable keywords |
| `filename` | SVG filename |
| `url` | Direct raw GitHub URL to the SVG |

### Example Entry

```json
{
  "id": "lakehouse",
  "name": "Lakehouse",
  "description": "Lakehouse database built over a data lake for big data processing with Apache Spark and SQL",
  "tags": ["data", "lakehouse", "storage"],
  "filename": "lakehouse_48_item.svg",
  "url": "https://raw.githubusercontent.com/AlahmadiQ8/icons/main/icons/lakehouse_48_item.svg"
}
```

### Agent Usage

1. Fetch `index.json` from the raw URL above
2. Search by `id`, `name`, `tags`, or `description` to find the right icon
3. Use the `url` field directly as an image source

## Icon Source

Icons are from the official [`@fabric-msft/svg-icons`](https://www.npmjs.com/package/@fabric-msft/svg-icons) package — the same icons used in the Microsoft Fabric product.

## Regenerating the Index

```bash
python3 scripts/build_index.py
```

This scans `icons/`, groups SVGs by concept, selects one representative per concept (preferring color/filled styles at 48px), and merges curated descriptions from `descriptions.json`.
