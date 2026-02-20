#!/usr/bin/env python3
"""MCP Server for Azure Icons.

Provides tools to search, browse, and fetch official Microsoft Azure and Fabric
SVG icons for use in architecture diagrams, documentation, and UI.
"""

import json
import re
from contextlib import asynccontextmanager
from difflib import SequenceMatcher
from importlib import resources
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_icons: list[dict] = []
_icons_by_id: dict[str, dict] = {}
_categories: dict[str, list[dict]] = {}


def _load_index() -> None:
    """Load the bundled index.json into module-level caches."""
    global _icons, _icons_by_id, _categories
    data_file = resources.files("azure_icons_mcp").joinpath("data", "index.json")
    raw = json.loads(data_file.read_text(encoding="utf-8"))
    _icons = raw["icons"]
    _icons_by_id = {icon["id"]: icon for icon in _icons}

    # Build category map from description parenthetical, e.g. "(databases)"
    _categories.clear()
    for icon in _icons:
        desc = icon.get("description", "")
        cat = "other"
        if "(" in desc and ")" in desc:
            cat = desc[desc.rfind("(") + 1 : desc.rfind(")")]
        _categories.setdefault(cat, []).append(icon)


# ---------------------------------------------------------------------------
# Search helpers (ported from search_icons.py)
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())


def _score_icon(icon: dict, terms: list[str]) -> float:
    fields = [
        (icon["id"], 3.0),
        (icon["name"], 2.5),
        (" ".join(icon.get("tags", [])), 2.0),
        (icon.get("description", ""), 1.0),
    ]
    texts = []
    for field, weight in fields:
        norm = _normalize(field)
        texts.append((norm, weight))
        no_spaces = norm.replace(" ", "")
        if no_spaces != norm:
            texts.append((no_spaces, weight * 0.9))

    total = 0.0
    for term in terms:
        best = 0.0
        for text, weight in texts:
            if term in text:
                best = max(best, weight * 1.0)
                continue
            words = text.split() if " " in text else [text]
            for word in words:
                ratio = SequenceMatcher(None, term, word).ratio()
                if ratio >= 0.7:
                    best = max(best, weight * ratio)
        if best == 0:
            return 0  # all terms must match
        total += best
    return total


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(server: FastMCP):
    _load_index()
    yield {}


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "azure_icons_mcp",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class SearchInput(BaseModel):
    """Input for searching icons by keyword."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(
        ...,
        description="Search query to match against icon names, IDs, tags, and descriptions (e.g. 'cosmos db', 'virtual machine', 'key vault')",
        min_length=1,
        max_length=200,
    )
    limit: Optional[int] = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=50,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class GetIconInput(BaseModel):
    """Input for getting a specific icon by ID."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    icon_id: str = Field(
        ...,
        description="The icon ID (e.g. 'azure_cosmos_db', 'lakehouse', 'virtual_machines')",
        min_length=1,
        max_length=200,
    )


class BrowseInput(BaseModel):
    """Input for browsing icons with optional category filter."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    category: Optional[str] = Field(
        default=None,
        description="Filter by category (e.g. 'databases', 'compute', 'networking', 'security'). Omit to list all icons.",
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum number of results to return",
        ge=1,
        le=100,
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip for pagination",
        ge=0,
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="azure_icons_search",
    annotations={
        "title": "Search Azure Icons",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def azure_icons_search(params: SearchInput) -> list[dict]:
    """Search for Azure and Fabric icons by keyword with fuzzy matching.

    Searches across icon IDs, names, tags, and descriptions. Supports partial
    matches and typo tolerance. All search terms must match at least one field.

    Args:
        params (SearchInput): Validated input containing:
            - query (str): Search keywords (e.g. "cosmos db", "key vault", "lakehouse")
            - limit (Optional[int]): Max results, 1-50, default 10

    Returns:
        list[dict]: Matching icons, each with id, name, description,
             tags, filename, and url. Empty list if no matches.
    """
    terms = _normalize(params.query).split()
    if not terms:
        return []

    scored = []
    for icon in _icons:
        score = _score_icon(icon, terms)
        if score > 0:
            scored.append((score, icon))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [icon for _, icon in scored[: params.limit]]


@mcp.tool(
    name="azure_icons_get",
    annotations={
        "title": "Get Azure Icon by ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def azure_icons_get(params: GetIconInput) -> dict | str:
    """Get a specific icon by its exact ID.

    Returns full icon metadata including the raw GitHub URL for embedding
    in HTML or downloading for PPTX diagrams.

    Args:
        params (GetIconInput): Validated input containing:
            - icon_id (str): Exact icon ID (e.g. "azure_cosmos_db", "lakehouse")

    Returns:
        dict: Icon details (id, name, description, tags, filename, url),
              or error string if icon is not found.
    """
    icon = _icons_by_id.get(params.icon_id)
    if icon:
        return icon
    return f"Error: Icon '{params.icon_id}' not found. Use azure_icons_search to find the correct ID."


@mcp.tool(
    name="azure_icons_list_categories",
    annotations={
        "title": "List Icon Categories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def azure_icons_list_categories() -> dict:
    """List all available icon categories with their icon counts.

    Categories are derived from icon descriptions and include areas like
    compute, networking, databases, security, ai + machine learning, etc.

    Returns:
        dict: Category names mapped to icon counts, sorted by count descending.
    """
    result = {cat: len(icons) for cat, icons in _categories.items()}
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


@mcp.tool(
    name="azure_icons_browse",
    annotations={
        "title": "Browse Azure Icons",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def azure_icons_browse(params: BrowseInput) -> dict | str:
    """Browse icons with optional category filter and pagination.

    Use azure_icons_list_categories first to see available categories,
    then browse a specific category, or omit category to page through all icons.

    Args:
        params (BrowseInput): Validated input containing:
            - category (Optional[str]): Category filter (e.g. "databases", "compute")
            - limit (Optional[int]): Max results per page, 1-100, default 20
            - offset (Optional[int]): Skip N results for pagination, default 0

    Returns:
        dict: Object with total count, current page of icons, and pagination info.
    """
    if params.category:
        cat_lower = params.category.lower()
        source = None
        for cat, icons in _categories.items():
            if cat.lower() == cat_lower:
                source = icons
                break
        if source is None:
            available = ", ".join(sorted(_categories.keys()))
            return f"Error: Category '{params.category}' not found. Available: {available}"
    else:
        source = _icons

    total = len(source)
    page = source[params.offset : params.offset + params.limit]
    has_more = total > params.offset + len(page)

    return {
        "total": total,
        "count": len(page),
        "offset": params.offset,
        "has_more": has_more,
        "next_offset": params.offset + len(page) if has_more else None,
        "icons": page,
    }
