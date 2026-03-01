"""
Project intelligence builder for methodology recommendation.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


SECTOR_ENUM = {
    "energy": "Energy",
    "transport": "Transport",
    "waste": "Waste",
    "afolu": "AFOLU",
    "industrial": "Industrial",
    "buildings": "Buildings",
    "cross-cutting": "Cross-cutting",
}


def build_project_intelligence(
    project_description: str,
    extracted_context: Dict[str, Any],
    llm: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Build normalized project intelligence summary.
    Uses LLM when provided; falls back to deterministic heuristics.
    """
    description = (project_description or "").strip()
    context = extracted_context or {}

    if llm is not None:
        llm_result = _build_with_llm(description, context, llm)
        if llm_result:
            return _normalize_intelligence(llm_result, description, context)

    heuristic = _build_heuristic(description, context)
    return _normalize_intelligence(heuristic, description, context)


def _build_with_llm(description: str, context: Dict[str, Any], llm: Any) -> Optional[Dict[str, Any]]:
    """Attempt JSON-only extraction via provided LLM model object."""
    schema_hint = {
        "summary": "string <=60 words",
        "sector": "Energy|Transport|Waste|AFOLU|Industrial|Buildings|Cross-cutting|null",
        "project_type": "string|null",
        "mechanism": "string|null",
        "ghg_sources": ["string"],
        "grid_connected": "boolean|null",
        "new_build": "boolean|null",
        "data_availability": {
            "metering": "boolean|null",
            "fuel_use_records": "boolean|null",
            "baseline_data": "boolean|null",
        },
        "constraints": ["string"],
        "assumptions": ["string"],
        "confidence": {
            "sector": "0..1",
            "project_type": "0..1",
            "mechanism": "0..1",
        },
    }

    prompt = (
        "Return ONLY valid JSON. Infer a normalized project intelligence object.\n"
        f"Schema: {json.dumps(schema_hint)}\n"
        f"Project description:\n{description}\n\n"
        f"Extracted context:\n{json.dumps(context, ensure_ascii=True)}"
    )
    try:
        response = llm.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        cleaned = _strip_code_fences(text)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


def _build_heuristic(description: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic heuristic extraction when LLM is unavailable."""
    d = description.lower()
    category = str(context.get("category", "")).lower()
    project_type = context.get("project_type")

    sector = _infer_sector(d, category, project_type)
    mechanism = _infer_mechanism(d, sector)

    ghg_sources: List[str] = []
    if any(k in d for k in ("methane", "ch4", "landfill", "manure")):
        ghg_sources.append("CH4")
    if any(k in d for k in ("nitrous", "n2o", "fertilizer")):
        ghg_sources.append("N2O")
    if any(k in d for k in ("co2", "carbon", "fuel", "electricity", "diesel", "petrol", "cement")):
        ghg_sources.append("CO2")
    ghg_sources = sorted(set(ghg_sources))

    grid_connected: Optional[bool] = None
    if any(k in d for k in ("grid connected", "grid-connected", "connected to grid", "export to grid")):
        grid_connected = True
    elif any(k in d for k in ("off-grid", "standalone", "mini-grid")):
        grid_connected = False

    new_build: Optional[bool] = None
    if any(k in d for k in ("install", "installation", "new", "develop", "construction", "build")):
        new_build = True
    elif any(k in d for k in ("retrofit", "existing", "upgrade", "rehabilitate")):
        new_build = False

    metering: Optional[bool] = None
    if any(k in d for k in ("meter", "metering", "smart meter", "revenue-grade")):
        metering = True

    fuel_records: Optional[bool] = None
    if any(k in d for k in ("fuel", "diesel", "gasoline", "petrol", "biomass consumption records")):
        fuel_records = True

    baseline_data: Optional[bool] = None
    if any(k in d for k in ("baseline", "historical", "prior year", "counterfactual", "reference scenario")):
        baseline_data = True

    constraints: List[str] = []
    if any(k in d for k in ("small-scale", "up to 15 mw", "15 mw")):
        constraints.append("Potential small-scale capacity or methodology threshold")
    if "not required by law" in d:
        constraints.append("Additionality may rely on regulatory surplus")

    assumptions: List[str] = []
    if sector is None:
        assumptions.append("Sector inferred as unknown due to limited specific indicators.")
    if mechanism is None:
        assumptions.append("Mechanism left null because reduction/removal/avoidance signal is weak.")
    if metering is None:
        assumptions.append("Metering availability not explicit in the provided description.")
    if baseline_data is None:
        assumptions.append("Baseline data availability not explicitly stated.")

    summary = _make_summary(description, context)

    return {
        "summary": summary,
        "sector": sector,
        "project_type": project_type,
        "mechanism": mechanism,
        "ghg_sources": ghg_sources,
        "grid_connected": grid_connected,
        "new_build": new_build,
        "data_availability": {
            "metering": metering,
            "fuel_use_records": fuel_records,
            "baseline_data": baseline_data,
        },
        "constraints": constraints,
        "assumptions": assumptions,
        "confidence": {
            "sector": 0.8 if sector else 0.2,
            "project_type": 0.75 if project_type else 0.25,
            "mechanism": 0.7 if mechanism else 0.3,
        },
    }


def _infer_sector(description_lower: str, context_category: str, project_type: Optional[str]) -> Optional[str]:
    """Map text/context into normalized sector enum."""
    raw = " ".join([description_lower, context_category, str(project_type or "").lower()])

    if any(k in raw for k in ("ev", "electric vehicle", "transport", "charging", "fleet")):
        return "Transport"
    if any(k in raw for k in ("solar", "wind", "hydro", "renewable electricity", "power generation")):
        return "Energy"
    if any(k in raw for k in ("waste", "landfill", "compost", "anaerobic digestion")):
        return "Waste"
    if any(k in raw for k in ("forest", "afforestation", "reforestation", "redd", "cropland", "soil", "wetland", "mangrove", "seagrass", "biochar", "agriculture")):
        return "AFOLU"
    if any(k in raw for k in ("cement", "concrete", "industrial", "mineralization", "manufacturing")):
        return "Industrial"
    if any(k in raw for k in ("cookstove", "household", "building energy", "efficiency retrofit")):
        return "Buildings"
    return None


def _infer_mechanism(description_lower: str, sector: Optional[str]) -> Optional[str]:
    """Infer high-level carbon mechanism."""
    if any(k in description_lower for k in ("sequestration", "carbon stock", "planting", "restoration", "biochar", "mineralization")):
        return "removal"
    if any(k in description_lower for k in ("avoided deforestation", "avoidance", "prevented", "diverting")):
        return "avoidance"
    if any(k in description_lower for k in ("displacing", "efficiency", "reduction", "electrification", "renewable")):
        return "emission_reduction"
    if sector in {"Transport", "Energy", "Waste", "Buildings", "Industrial"}:
        return "emission_reduction"
    return None


def _make_summary(description: str, context: Dict[str, Any]) -> str:
    """Create <=60 word summary from available inputs."""
    project_name = context.get("project_name") or "Project"
    project_type = context.get("project_type") or "carbon activity"
    country = (context.get("location") or {}).get("country") or "unspecified location"
    annual = (context.get("carbon_metrics") or {}).get("annual_reductions")

    summary = (
        f"{project_name} is a {project_type.lower()} in {country}. "
        f"It targets emission benefits through defined project activities"
        + (f", with about {annual} tCO2e/year expected reductions." if annual else ".")
    )
    return _limit_words(summary, 60)


def _normalize_intelligence(raw: Dict[str, Any], description: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate output schema."""
    data = raw if isinstance(raw, dict) else {}
    summary = _limit_words(str(data.get("summary") or _make_summary(description, context)), 60)

    sector = data.get("sector")
    if isinstance(sector, str):
        sector = sector.strip()
        sector_key = sector.lower()
        sector = SECTOR_ENUM.get(sector_key, sector if sector in SECTOR_ENUM.values() else None)
    else:
        sector = None

    data_availability = data.get("data_availability") if isinstance(data.get("data_availability"), dict) else {}

    normalized = {
        "summary": summary,
        "sector": sector,
        "project_type": _none_or_str(data.get("project_type")),
        "mechanism": _none_or_str(data.get("mechanism")),
        "ghg_sources": _as_string_list(data.get("ghg_sources")),
        "grid_connected": _as_optional_bool(data.get("grid_connected")),
        "new_build": _as_optional_bool(data.get("new_build")),
        "data_availability": {
            "metering": _as_optional_bool(data_availability.get("metering")),
            "fuel_use_records": _as_optional_bool(
                data_availability.get("fuel_use_records", data_availability.get("fuel_records"))
            ),
            "baseline_data": _as_optional_bool(data_availability.get("baseline_data")),
        },
        "constraints": _as_string_list(data.get("constraints")),
        "assumptions": _as_string_list(data.get("assumptions")),
        "confidence": {
            "sector": _bounded_float((data.get("confidence") or {}).get("sector"), 0.0, 1.0, 0.2),
            "project_type": _bounded_float((data.get("confidence") or {}).get("project_type"), 0.0, 1.0, 0.2),
            "mechanism": _bounded_float((data.get("confidence") or {}).get("mechanism"), 0.0, 1.0, 0.2),
        },
    }

    if not normalized["assumptions"] and not description:
        normalized["assumptions"].append("Project description was empty.")

    return normalized


def _as_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _none_or_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _as_optional_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def _bounded_float(value: Any, min_value: float, max_value: float, default: float) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    return max(min_value, min(max_value, number))


def _limit_words(text: str, max_words: int) -> str:
    words = re.findall(r"\S+", text or "")
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words])


def _strip_code_fences(text: str) -> str:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned
