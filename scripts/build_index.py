#!/usr/bin/env python3
"""Build index.json from icons/ directory.

Groups SVG files by concept and selects one representative per concept,
preferring color > filled > item styles at 48px size.
Merges curated descriptions from descriptions.json when available.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = "AlahmadiQ8/icons"
BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/icons"

ROOT_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT_DIR / "icons"
DESCRIPTIONS_FILE = ROOT_DIR / "descriptions.json"
OUTPUT_FILE = ROOT_DIR / "index.json"
SKILL_INDEX_FILE = ROOT_DIR / "skills" / "azure-icons" / "references" / "index.json"
MCP_INDEX_FILE = ROOT_DIR / "mcp-server" / "src" / "azure_icons_mcp" / "data" / "index.json"

# Style priority: lower index = higher priority
STYLE_PRIORITY = {
    "color": 0,
    "filled": 1,
    "item": 2,
    "regular": 3,
    "non-item": 4,
    "items": 5,
    "filled_multi-color": 6,
    "regular_multi-color": 7,
    "dark_multi-color": 8,
    "light_multi-color": 9,
    "multi-color": 10,
}

PREFERRED_SIZE = 48

VALID_SIZES = {"12", "16", "20", "24", "28", "32", "40", "48", "64"}

KNOWN_STYLES = {
    "color", "filled", "regular", "item", "items", "non-item",
    "multi-color", "filled_multi-color", "regular_multi-color",
    "dark_multi-color", "light_multi-color",
    "filed", "fille",  # typos in source files
}

# Regex to parse filenames like: concept_size_style.svg
# The concept can contain underscores, so we anchor on known sizes and styles.
FILENAME_RE = re.compile(
    r"^(?P<concept>.+)_(?P<size>\d+)(px)?_(?P<style>[a-z][a-z0-9_-]*)\.svg$",
    re.IGNORECASE,
)


def parse_filename(filename: str) -> dict | None:
    m = FILENAME_RE.match(filename)
    if not m:
        return None
    size = m.group("size")
    style = m.group("style")
    if size not in VALID_SIZES or style not in KNOWN_STYLES:
        return None
    # Normalize typo styles to 'filled'
    if style in ("filed", "fille"):
        style = "filled"
    return {
        "concept": m.group("concept"),
        "size": int(size),
        "style": style,
        "filename": filename,
    }


def concept_to_name(concept: str) -> str:
    """Convert snake_case concept to Title Case name."""
    return " ".join(w.capitalize() for w in concept.split("_"))


def concept_to_description(concept: str) -> str:
    """Auto-derive a basic description from concept name."""
    name = concept_to_name(concept)
    return f"{name} icon"


def pick_best_variant(variants: list[dict]) -> dict:
    """Pick the best variant from a list using style and size priority."""

    def sort_key(v):
        style_rank = STYLE_PRIORITY.get(v["style"], 99)
        # Prefer PREFERRED_SIZE, then closest larger, then closest smaller
        size_diff = abs(v["size"] - PREFERRED_SIZE)
        size_exact = 0 if v["size"] == PREFERRED_SIZE else 1
        return (style_rank, size_exact, size_diff)

    variants.sort(key=sort_key)
    return variants[0]


def load_descriptions() -> dict:
    if DESCRIPTIONS_FILE.exists():
        with open(DESCRIPTIONS_FILE) as f:
            return json.load(f)
    return {}


def build_tags(concept: str, description: str) -> list[str]:
    """Generate searchable tags from concept and description."""
    tags = set()
    # Add each word from the concept as a tag
    for word in concept.split("_"):
        if len(word) > 1:
            tags.add(word.lower())

    # Add category tags based on common patterns
    category_map = {
        "arrow": "navigation",
        "database": "data",
        "data": "data",
        "table": "data",
        "document": "document",
        "notebook": "document",
        "diagram": "diagram",
        "chart": "visualization",
        "gauge": "visualization",
        "graph": "visualization",
        "bar": "visualization",
        "pie": "visualization",
        "calendar": "scheduling",
        "filter": "ui",
        "layout": "ui",
        "window": "ui",
        "rectangle": "ui",
        "square": "ui",
        "shapes": "design",
        "shape": "design",
        "copilot": "ai",
        "sparkle": "ai",
        "pipeline": "orchestration",
        "dataflow": "orchestration",
        "stream": "streaming",
        "event": "streaming",
        "fabric": "platform",
        "power_bi": "analytics",
        "report": "analytics",
        "dashboard": "analytics",
        "scorecard": "analytics",
        "lakehouse": "storage",
        "warehouse": "storage",
        "one_lake": "storage",
        "kql": "query",
        "sql": "query",
        "schema": "modeling",
        "model": "modeling",
        "semantic": "modeling",
        "person": "people",
        "people": "people",
        "library": "content",
        "folder": "organization",
        "lock": "security",
        "sensitivity": "security",
        "policy": "governance",
        "restriction": "governance",
    }

    for keyword, category in category_map.items():
        if keyword in concept:
            tags.add(category)

    return sorted(tags)


def main():
    # Scan icons directory
    files = [f for f in os.listdir(ICONS_DIR) if f.endswith(".svg")]

    # Group by concept
    groups: dict[str, list[dict]] = {}
    skipped = []
    for f in files:
        parsed = parse_filename(f)
        if parsed:
            groups.setdefault(parsed["concept"], []).append(parsed)
        else:
            skipped.append(f)

    if skipped:
        print(f"Warning: {len(skipped)} files skipped (couldn't parse):")
        for s in skipped[:10]:
            print(f"  {s}")

    # Load curated descriptions
    descriptions = load_descriptions()

    # Build index
    icons = []
    for concept in sorted(groups.keys()):
        variants = groups[concept]
        best = pick_best_variant(variants)
        desc = descriptions.get(concept, concept_to_description(concept))
        tags = build_tags(concept, desc)

        icons.append({
            "id": concept,
            "name": concept_to_name(concept),
            "description": desc,
            "tags": tags,
            "filename": best["filename"],
            "url": f"{BASE_URL}/{best['filename']}",
        })

    index = {
        "metadata": {
            "description": "Microsoft Fabric icon index for coding agent consumption",
            "source": "Official Microsoft Fabric Icons (@fabric-msft/svg-icons)",
            "repo": REPO,
            "base_url": BASE_URL,
            "total_icons": len(icons),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "icons": icons,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(index, f, indent=2)

    # Also copy into the skill if the directory exists
    if SKILL_INDEX_FILE.parent.exists():
        import shutil
        shutil.copy2(OUTPUT_FILE, SKILL_INDEX_FILE)
        print(f"Copied index to {SKILL_INDEX_FILE}")

    # Also copy into the MCP server package if the directory exists
    if MCP_INDEX_FILE.parent.exists():
        import shutil
        shutil.copy2(OUTPUT_FILE, MCP_INDEX_FILE)
        print(f"Copied index to {MCP_INDEX_FILE}")

    print(f"Generated {OUTPUT_FILE} with {len(icons)} icons")


if __name__ == "__main__":
    main()
