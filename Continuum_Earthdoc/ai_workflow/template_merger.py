"""
Deterministic multi-methodology template merger.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Tuple, Optional

from knowledge.methodology_templates import METHODOLOGY_SECTION_TEMPLATES


def merge_methodology_templates(
    primary_code: str,
    additional_codes: List[str],
    templates: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Merge methodology templates into a deterministic combined section list.
    """
    templates = templates or METHODOLOGY_SECTION_TEMPLATES
    if primary_code not in templates:
        raise ValueError(f"Primary methodology template not found: {primary_code}")

    normalized_additional = [c for c in additional_codes if c and c != primary_code]
    for code in normalized_additional:
        if code not in templates:
            raise ValueError(f"Additional methodology template not found: {code}")

    combined_sections: List[Dict[str, Any]] = []
    section_index: Dict[str, int] = {}
    conflicts: List[Dict[str, Any]] = []

    def ingest_template(method_code: str, is_primary: bool) -> None:
        template = templates[method_code]
        for section_group in template.get("sections", []):
            group_number = section_group.get("number", "")
            group_title = section_group.get("title", "")
            for subsection in section_group.get("subsections", []):
                normalized = _build_normalized_subsection(
                    subsection=subsection,
                    method_code=method_code,
                    group_number=group_number,
                    group_title=group_title,
                    primary_code=primary_code,
                    additional_only=(not is_primary),
                )
                key = normalized["section_id"]
                if key in section_index:
                    idx = section_index[key]
                    existing = combined_sections[idx]
                    merge_conflicts = _merge_existing_section(existing, normalized, method_code, primary_code)
                    conflicts.extend(merge_conflicts)
                else:
                    section_index[key] = len(combined_sections)
                    combined_sections.append(normalized)

    ingest_template(primary_code, is_primary=True)
    for code in normalized_additional:
        ingest_template(code, is_primary=False)

    merge_report = {
        "primary_methodology": primary_code,
        "additional_methodologies": normalized_additional,
        "combined_methodologies": [primary_code] + normalized_additional,
        "total_sections": len(combined_sections),
        "conflicts_count": len(conflicts),
        "conflicts": conflicts,
        "resolution_policy": {
            "section_key": "section_id if present else normalized title slug",
            "merge_order": "primary-first, then additional methodologies in provided order",
            "field_collision": "keep primary field prompt, store alternatives in field_variants",
            "narrative_collision": "keep primary narrative scaffold, store alternatives in narrative_variants",
            "metrics_collision": "union metrics; tag duplicates with source methodology",
            "new_sections": "append with '(Additional Methodology: CODE)' label and appendix placement",
        },
    }
    return combined_sections, merge_report


def _build_normalized_subsection(
    subsection: Dict[str, Any],
    method_code: str,
    group_number: str,
    group_title: str,
    primary_code: str,
    additional_only: bool,
) -> Dict[str, Any]:
    section_title = subsection.get("title", "")
    section_id = subsection.get("section_id") or _slugify(section_title)
    fields = copy.deepcopy(subsection.get("fields") or _infer_fields_from_title(section_title, method_code))
    narrative_scaffold = subsection.get("narrative_scaffold", f"Provide detailed information for {section_title}.")
    metrics = copy.deepcopy(subsection.get("metrics", {}))

    title = section_title
    placement = "main"
    if additional_only:
        title = f"{section_title} (Additional Methodology: {method_code})"
        placement = "additional_appendix"

    return {
        "num": subsection.get("num", ""),
        "title": title,
        "base_title": section_title,
        "required": bool(subsection.get("required", True)),
        "section_id": section_id,
        "group_number": group_number,
        "group_title": group_title,
        "fields": fields,
        "narrative_scaffold": narrative_scaffold,
        "metrics": metrics,
        "placement": placement,
        "provenance": {
            "source_methodologies": [method_code],
            "primary_owner": primary_code,
        },
        "conflicts": [],
        "variants": {
            "title_variants": {},
            "field_variants": {},
            "narrative_variants": {},
            "metrics_variants": {},
        },
    }


def _merge_existing_section(
    existing: Dict[str, Any],
    incoming: Dict[str, Any],
    incoming_code: str,
    primary_code: str,
) -> List[Dict[str, Any]]:
    """Merge incoming section into existing one deterministically."""
    conflicts: List[Dict[str, Any]] = []

    # Provenance
    sources = existing["provenance"]["source_methodologies"]
    if incoming_code not in sources:
        sources.append(incoming_code)

    # Title variant
    if existing.get("base_title") != incoming.get("base_title"):
        existing["variants"]["title_variants"][incoming_code] = incoming.get("base_title")
        conflicts.append(
            {
                "section_id": existing["section_id"],
                "type": "title_variant",
                "policy": "primary wording preserved; alternative title stored",
                "source": incoming_code,
            }
        )

    # Fields union with collision variants
    for field_name, incoming_field_def in incoming.get("fields", {}).items():
        if field_name not in existing["fields"]:
            existing["fields"][field_name] = incoming_field_def
        else:
            existing_field = existing["fields"][field_name]
            if not _field_defs_equal(existing_field, incoming_field_def):
                existing["variants"]["field_variants"].setdefault(field_name, {})
                existing["variants"]["field_variants"][field_name][incoming_code] = incoming_field_def
                conflicts.append(
                    {
                        "section_id": existing["section_id"],
                        "type": "field_collision",
                        "field": field_name,
                        "policy": "primary/default field prompt preserved; variant stored by methodology",
                        "source": incoming_code,
                    }
                )

    # Narrative variants
    existing_scaffold = (existing.get("narrative_scaffold") or "").strip()
    incoming_scaffold = (incoming.get("narrative_scaffold") or "").strip()
    if incoming_scaffold and incoming_scaffold != existing_scaffold:
        existing["variants"]["narrative_variants"][incoming_code] = incoming_scaffold
        conflicts.append(
            {
                "section_id": existing["section_id"],
                "type": "narrative_collision",
                "policy": "primary narrative scaffold preserved; variant stored",
                "source": incoming_code,
            }
        )

    # Metrics union with tagged duplicates
    for metric_name, metric_def in incoming.get("metrics", {}).items():
        if metric_name not in existing["metrics"]:
            existing["metrics"][metric_name] = metric_def
        else:
            if existing["metrics"][metric_name] != metric_def:
                tagged_name = f"{metric_name}__{incoming_code}"
                existing["metrics"][tagged_name] = metric_def
                existing["variants"]["metrics_variants"].setdefault(metric_name, {})
                existing["variants"]["metrics_variants"][metric_name][incoming_code] = metric_def
                conflicts.append(
                    {
                        "section_id": existing["section_id"],
                        "type": "metric_collision",
                        "metric": metric_name,
                        "policy": "keep both definitions with source tag",
                        "source": incoming_code,
                    }
                )

    # Keep primary placement if already main
    if existing.get("placement") != "main" and incoming_code == primary_code:
        existing["placement"] = "main"

    existing["conflicts"].extend(conflicts)
    return conflicts


def _slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "section"


def _field_defs_equal(left: Dict[str, Any], right: Dict[str, Any]) -> bool:
    """Compare two field definitions consistently."""
    return (
        str(left.get("type", "string")) == str(right.get("type", "string"))
        and bool(left.get("required", False)) == bool(right.get("required", False))
        and str(left.get("hint", "")) == str(right.get("hint", ""))
        and str(left.get("default", "")) == str(right.get("default", ""))
    )


def _infer_fields_from_title(title: str, method_code: str) -> Dict[str, Dict[str, Any]]:
    """Deterministic base field inference (matches existing workflow behavior)."""
    fields = {
        "content": {
            "type": "textarea",
            "required": True,
            "hint": f"Provide detailed information for {title} ({method_code})",
        }
    }
    title_lower = (title or "").lower()

    if "proponent" in title_lower:
        fields.update(
            {
                "company_name": {"type": "string", "required": True, "hint": "Legal name of organization"},
                "contact_person": {"type": "string", "required": False},
                "email": {"type": "string", "required": False},
                "phone": {"type": "string", "required": False},
            }
        )
    elif "location" in title_lower:
        fields.update(
            {
                "country": {"type": "string", "required": True},
                "region": {"type": "string", "required": False},
                "city": {"type": "string", "required": False},
                "coordinates": {"type": "string", "required": False, "hint": "Latitude, Longitude"},
            }
        )
    elif "date" in title_lower:
        fields.update({"start_date": {"type": "string", "required": True, "hint": "YYYY-MM-DD format"}})
    elif "crediting period" in title_lower:
        fields.update(
            {
                "duration_years": {"type": "number", "required": True, "hint": "Length in years"},
                "start_date": {"type": "string", "required": True},
                "end_date": {"type": "string", "required": True},
            }
        )
    elif "emission" in title_lower and "reduction" in title_lower:
        fields.update(
            {
                "annual_reductions": {"type": "number", "required": True, "hint": "tCO2e per year"},
                "total_reductions": {"type": "number", "required": True, "hint": "tCO2e over crediting period"},
            }
        )
    return fields
