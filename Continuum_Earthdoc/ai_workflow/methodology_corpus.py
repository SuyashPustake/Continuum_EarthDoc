"""
Methodology corpus utilities and card construction.
"""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import copy
from functools import lru_cache
from typing import Any, Dict, List, Optional

from agents.pdd_agent import METHODOLOGY_DATABASE


_CACHE_DIR = ".cache"
_EMBEDDING_CACHE_FILE = os.path.join(_CACHE_DIR, "methodology_embeddings.pkl")


def get_methodology_cards() -> List[Dict[str, Any]]:
    """Build normalized methodology cards used for semantic retrieval."""
    return copy.deepcopy(_get_methodology_cards_cached())


@lru_cache(maxsize=1)
def _get_methodology_cards_cached() -> List[Dict[str, Any]]:
    """Cached card computation."""
    cards: List[Dict[str, Any]] = []
    for code in sorted(METHODOLOGY_DATABASE.keys()):
        method = METHODOLOGY_DATABASE[code]
        title = method.get("title", code)
        category = method.get("category", "Unknown")
        description = method.get("description", "")
        applicability = method.get("applicability", []) or []
        key_parameters = method.get("key_parameters", []) or []
        monitored = [p.get("name", "") for p in key_parameters if p.get("monitored")]

        metadata = _build_metadata(code, method)
        card_text = (
            f"{code} | {title}\n"
            f"Category: {category}\n"
            f"Description: {description}\n"
            f"Applicability: {'; '.join(str(a) for a in applicability[:5])}\n"
            f"Monitoring: {', '.join(monitored[:6]) if monitored else 'Not specified'}\n"
            f"Eligibility: {'; '.join(metadata.get('eligibility', []))}\n"
            f"Exclusions: {'; '.join(metadata.get('exclusions', []))}"
        )

        cards.append(
            {
                "code": code,
                "name": title,
                "category": category,
                "card_text": card_text,
                "metadata": metadata,
            }
        )
    return cards


def corpus_hash(cards: Optional[List[Dict[str, Any]]] = None) -> str:
    """Stable hash for a given corpus version."""
    cards = cards or get_methodology_cards()
    payload = [{"code": c["code"], "card_text": c["card_text"]} for c in cards]
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_cached_embeddings(version_hash: str, backend: str) -> Optional[Dict[str, List[float]]]:
    """Load cached embeddings keyed by corpus hash and backend."""
    if not os.path.exists(_EMBEDDING_CACHE_FILE):
        return None
    try:
        with open(_EMBEDDING_CACHE_FILE, "rb") as f:
            payload = pickle.load(f)
        return payload.get(version_hash, {}).get(backend)
    except Exception:
        return None


def save_cached_embeddings(version_hash: str, backend: str, vectors: Dict[str, List[float]]) -> None:
    """Persist embeddings cache."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    payload: Dict[str, Any] = {}
    if os.path.exists(_EMBEDDING_CACHE_FILE):
        try:
            with open(_EMBEDDING_CACHE_FILE, "rb") as f:
                payload = pickle.load(f)
        except Exception:
            payload = {}
    payload.setdefault(version_hash, {})
    payload[version_hash][backend] = vectors
    with open(_EMBEDDING_CACHE_FILE, "wb") as f:
        pickle.dump(payload, f)


def _build_metadata(code: str, method: Dict[str, Any]) -> Dict[str, Any]:
    """Methodology-specific metadata for deterministic guardrails."""
    category = method.get("category", "")
    description = (method.get("description", "") or "").lower()
    applicability = method.get("applicability", []) or []

    base = {
        "sector": _sector_from_category(category, description),
        "mechanism": _mechanism_from_text(description, applicability),
        "grid_connected_required": False,
        "requires_metering": False,
        "eligibility": applicability[:4],
        "exclusions": [],
        "disqualifier_keywords": [],
    }

    if code == "VM0038":
        base["grid_connected_required"] = True
        base["requires_metering"] = True
        base["disqualifier_keywords"] = ["internal combustion upgrade only", "no charging infrastructure"]
    elif code == "AMS-I.D":
        base["grid_connected_required"] = True
        base["requires_metering"] = True
        base["disqualifier_keywords"] = ["off-grid only"]
    elif code == "VM0048":
        base["exclusions"] = ["No credible deforestation/degradation threat in baseline"]
    elif code == "VM0047":
        base["exclusions"] = ["Land has been forest recently", "Native ecosystem conversion"]
    elif code == "VM0043":
        base["requires_metering"] = True
    elif code == "AMS-III.E":
        base["exclusions"] = ["Organic waste not landfill-bound in baseline"]

    return base


def _sector_from_category(category: str, description: str) -> str:
    cat = (category or "").lower()
    text = f"{cat} {description}"
    if any(k in text for k in ("transport", "vehicle", "charging")):
        return "Transport"
    if any(k in text for k in ("energy", "renewable", "electricity")):
        return "Energy"
    if any(k in text for k in ("waste", "landfill")):
        return "Waste"
    if any(k in text for k in ("forestry", "agriculture", "blue carbon", "wetland", "biochar", "land use")):
        return "AFOLU"
    if any(k in text for k in ("industrial", "concrete", "cement")):
        return "Industrial"
    if any(k in text for k in ("cook", "household")):
        return "Buildings"
    return "Cross-cutting"


def _mechanism_from_text(description: str, applicability: List[str]) -> str:
    text = f"{description} {' '.join(str(a).lower() for a in applicability)}"
    if any(k in text for k in ("sequestration", "carbon stock", "restoration", "mineralization")):
        return "removal"
    if any(k in text for k in ("avoid", "avoiding", "diverting", "deforestation")):
        return "avoidance"
    return "emission_reduction"
