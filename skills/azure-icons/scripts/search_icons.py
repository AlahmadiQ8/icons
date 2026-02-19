#!/usr/bin/env python3
"""Search Microsoft Fabric icons by keyword with fuzzy matching. Returns matching icons as JSON."""

import json
import os
import re
import sys
from difflib import SequenceMatcher

def _normalize(text: str) -> str:
    """Normalize text: lowercase, collapse separators, strip non-alnum."""
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())

def _score_icon(icon: dict, terms: list[str]) -> float:
    """Score an icon against search terms. Returns 0 if no match, higher = better."""
    fields = [
        (icon["id"], 3.0),
        (icon["name"], 2.5),
        (" ".join(icon["tags"]), 2.0),
        (icon["description"], 1.0),
    ]

    # Build searchable text variants
    texts = []
    for field, weight in fields:
        norm = _normalize(field)
        texts.append((norm, weight))
        # Also add version without spaces for compound matching (e.g. "realtime" matches "real time")
        no_spaces = norm.replace(" ", "")
        if no_spaces != norm:
            texts.append((no_spaces, weight * 0.9))

    total_score = 0.0
    for term in terms:
        best_term_score = 0.0
        for text, weight in texts:
            # Exact substring match
            if term in text:
                best_term_score = max(best_term_score, weight * 1.0)
                continue
            # Fuzzy match: check each word in the text
            words = text.split() if " " in text else [text]
            for word in words:
                ratio = SequenceMatcher(None, term, word).ratio()
                if ratio >= 0.7:
                    best_term_score = max(best_term_score, weight * ratio)
        if best_term_score == 0:
            return 0  # All terms must match something
        total_score += best_term_score

    return total_score

def search(query: str, limit: int = 10) -> list[dict]:
    index_path = os.path.join(os.path.dirname(__file__), "..", "references", "index.json")
    with open(index_path) as f:
        data = json.load(f)

    terms = _normalize(query).split()
    if not terms:
        return []

    scored = []
    for icon in data["icons"]:
        score = _score_icon(icon, terms)
        if score > 0:
            scored.append((score, icon))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [icon for _, icon in scored[:limit]]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_icons.py <query> [limit]", file=sys.stderr)
        sys.exit(1)
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    results = search(query, limit)
    print(json.dumps(results, indent=2))
