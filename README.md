# Microsoft Fabric Icons

A structured icon repository for **coding agents** to easily discover and use official [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/) icons in diagrams, documentation, and UI.

## Quick Start (for Agents)

Fetch the icon index:

```
https://raw.githubusercontent.com/AlahmadiQ8/icons/main/index.json
```

The index contains 175 icons, each with:

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

## Maintainer Guide

### Adding New Icons

1. Drop SVG files into `icons/` following the naming convention:
   ```
   <concept>_<size>_<style>.svg
   ```
   - **concept**: snake_case name (e.g. `lakehouse`, `data_warehouse`)
   - **size**: 12, 16, 20, 24, 28, 32, 40, 48, or 64
   - **style**: `color`, `filled`, `regular`, `item`, `non-item`, etc.
   - Example: `my_new_item_48_color.svg`

2. Add a curated description in `descriptions.json`:
   ```json
   {
     "my_new_item": "Description of what this icon represents in Fabric"
   }
   ```
   If omitted, a generic description is auto-generated from the concept name.

3. Rebuild the index:
   ```bash
   python3 scripts/build_index.py
   ```
   This scans `icons/`, groups SVGs by concept, selects one representative per concept (preferring color/filled styles at 48px), merges curated descriptions from `descriptions.json`, and copies the result into the skill.

4. Commit and push both `index.json` and the new SVGs.

### Removing Icons

1. Delete the SVG files from `icons/`
2. Remove the entry from `descriptions.json`
3. Rebuild: `python3 scripts/build_index.py`

### Packaging the Skill

The skill at `skills/azure-icons/` is a self-contained package agents can install to search and fetch icons. After rebuilding the index:

```bash
python3 .claude/skills/skill-creator/scripts/package_skill.py skills/azure-icons ./skills
```

This validates and produces `skills/azure-icons.skill`.

The skill contains:
- `SKILL.md` — trigger description and usage instructions
- `references/index.json` — the full icon index (auto-copied by `build_index.py`)
- `scripts/search_icons.py` — fuzzy search script (agents run this instead of loading the full index)
