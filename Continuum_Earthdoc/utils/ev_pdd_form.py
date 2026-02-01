"""
EV PDD multistep form: load VCS EV template, collect user values, produce filled PDD.

Enterprise-grade: validated template loading, Jinja2 document assembly,
value normalization, and robust error handling. All changes preserve
objectives: multistep form → completed PDD document.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import date, datetime

try:
    from jinja2 import Template, Environment, Undefined

    class SilentUndefined(Undefined):
        """Jinja undefined that renders as empty string (no strict key requirement)."""
        def __str__(self) -> str:
            return ""

        def __iter__(self):
            return iter([])

        def __bool__(self) -> bool:
            return False

    _JINJA_AVAILABLE = True
except ImportError:
    _JINJA_AVAILABLE = False

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

TEMPLATE_PATH = Path(__file__).parent.parent / "knowledge" / "vcs_ev_pdd_template.json"
DEFAULT_FORM_STEPS_ORDER = [
    "cover", "section1", "section2", "section3", "section4",
    "section5", "section6", "section7", "appendices",
]
SECTION_LABELS: Dict[str, str] = {
    "cover": "Cover & Project Info",
    "section1": "Section 1: Project Details",
    "section2": "Section 2: Stakeholders",
    "section3": "Section 3: Methodology",
    "section4": "Section 4: Implementation",
    "section5": "Section 5: Quantification",
    "section6": "Section 6: Monitoring (Validation)",
    "section7": "Section 7: Monitoring (Report)",
    "appendices": "Appendix",
}


# -----------------------------------------------------------------------------
# Template loading and validation
# -----------------------------------------------------------------------------

def load_ev_pdd_template() -> Dict[str, Any]:
    """
    Load and validate the VCS EV PDD template JSON.
    Raises FileNotFoundError if template is missing, ValueError if invalid structure.
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"EV PDD template not found: {TEMPLATE_PATH}")
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid EV PDD template JSON: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("EV PDD template root must be a JSON object")
    if "cover" not in data:
        raise ValueError("EV PDD template must contain 'cover'")
    return data


def get_form_steps(template: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    """
    Return a flat list of (section_key, subsection_key, user_fields) for each step.
    Section keys: 'cover', 'section1'..'section7', 'appendices'.
    Subsection keys: 'cover', '1.1', '2.1', ..., 'appendix1', etc.
    """
    steps: List[Tuple[str, str, Dict[str, Any]]] = []
    order = template.get("_meta", {}).get("form_steps_order") or DEFAULT_FORM_STEPS_ORDER
    if not isinstance(order, list):
        order = DEFAULT_FORM_STEPS_ORDER

    # Cover (only if it has user_fields)
    cover = template.get("cover")
    if isinstance(cover, dict) and cover.get("user_fields"):
        steps.append(("cover", "cover", cover["user_fields"]))

    # Section blocks in order
    for sk in order:
        if sk in ("cover", "contents") or sk not in template:
            continue
        block = template[sk]
        if not isinstance(block, dict):
            continue
        for subsection_key, subsection_data in block.items():
            if subsection_key.startswith("_"):
                continue
            if isinstance(subsection_data, dict) and subsection_data.get("user_fields"):
                steps.append((sk, subsection_key, subsection_data["user_fields"]))

    return steps


def _section_sort_key(sub_key: str) -> Tuple[int, int]:
    """Sort subsection keys like 1.1, 1.2, 1.10 or appendix1 numerically."""
    if not sub_key or not isinstance(sub_key, str):
        return (0, 0)
    sub_key = sub_key.strip()
    if sub_key.startswith("appendix"):
        try:
            return (99, int(sub_key.replace("appendix", "").strip() or 0))
        except ValueError:
            return (99, 0)
    try:
        parts = sub_key.split(".")
        if len(parts) >= 2:
            return (int(parts[0]), int(parts[1]))
        return (int(parts[0]), 0)
    except (ValueError, TypeError, AttributeError):
        return (0, 0)


def get_step_label(section_key: str, subsection_key: str) -> str:
    """Human-readable label for a form step."""
    base = SECTION_LABELS.get(section_key, section_key)
    if section_key == "cover":
        return base
    return f"{base} — {subsection_key}"


# -----------------------------------------------------------------------------
# Value handling and state
# -----------------------------------------------------------------------------

def _default_for_field(field_spec: Dict[str, Any]) -> Any:
    """Default value for a field from its spec (type/default)."""
    if isinstance(field_spec, dict) and "default" in field_spec:
        return field_spec["default"]
    ftype = (field_spec or {}).get("type", "string")
    if ftype == "number":
        return None
    if ftype == "date":
        return None
    return ""


def _ensure_values_structure(values: Dict, section_key: str, subsection_key: str) -> None:
    """Ensure nested dict exists for section/subsection (mutates values)."""
    if not isinstance(values, dict):
        return
    if section_key == "cover":
        values.setdefault("cover", {})
        return
    values.setdefault(section_key, {})
    values[section_key].setdefault(subsection_key, {})


def get_current_values(
    values: Dict[str, Any],
    section_key: str,
    subsection_key: str,
    user_fields: Dict[str, Any],
) -> Dict[str, Any]:
    """Get current step values with defaults from field specs. Never mutates values."""
    out: Dict[str, Any] = {}
    if not user_fields:
        return out
    current: Dict[str, Any] = {}
    if section_key == "cover":
        current = (values or {}).get("cover") or {}
    else:
        current = ((values or {}).get(section_key) or {}).get(subsection_key) or {}
    for fname, fspec in user_fields.items():
        out[fname] = current.get(fname)
        if out[fname] is None:
            out[fname] = _default_for_field(fspec)
    return out


def set_current_values(
    values: Dict[str, Any],
    section_key: str,
    subsection_key: str,
    field_values: Dict[str, Any],
) -> None:
    """Write back collected field values for this step. Mutates values."""
    _ensure_values_structure(values, section_key, subsection_key)
    if section_key == "cover":
        values["cover"].update(field_values or {})
    else:
        values[section_key][subsection_key] = dict(field_values or {})


def _normalize_value(val: Any, ftype: str) -> Any:
    """Normalize a value for document rendering (strip strings, coerce types)."""
    if val is None:
        return None
    if ftype == "string":
        s = str(val).strip()
        return s if s else None
    if ftype == "number":
        try:
            return float(val) if val is not None else None
        except (TypeError, ValueError):
            return None
    if ftype == "date":
        if isinstance(val, (date, datetime)):
            return val.isoformat() if hasattr(val, "isoformat") else str(val)
        if isinstance(val, str) and val.strip():
            return val.strip()[:10]
        return None
    return val


# -----------------------------------------------------------------------------
# Document assembly (Jinja2 with fallback)
# -----------------------------------------------------------------------------

def _render_block_jinja(fixed_text: str, block_vals: Dict[str, Any]) -> str:
    """Render one block with Jinja2; undefined vars render as empty."""
    if not _JINJA_AVAILABLE:
        raise RuntimeError("Jinja2 is required for document assembly; install jinja2")
    env = Environment(undefined=SilentUndefined, autoescape=False)
    template = env.from_string(fixed_text)
    # Coerce values to strings for rendering; None -> ''
    safe_vals = {}
    for k, v in (block_vals or {}).items():
        if v is None:
            safe_vals[k] = ""
        elif isinstance(v, (date, datetime)):
            safe_vals[k] = v.isoformat() if hasattr(v, "isoformat") else str(v)
        else:
            safe_vals[k] = str(v)
    return template.render(**safe_vals)


def _render_block_fallback(fixed_text: str, block_vals: Dict[str, Any]) -> str:
    """Fallback: replace {{ key }} with value; strip remaining placeholders."""
    text = fixed_text or ""
    for key, val in (block_vals or {}).items():
        text = text.replace("{{" + str(key) + "}}", str(val) if val is not None else "")
    return re.sub(r"\{\{[^}]+\}\}", "", text)


def fill_document(template: Dict[str, Any], values: Dict[str, Any]) -> str:
    """
    Build the full PDD markdown from template and collected values.
    Uses Jinja2 when available; otherwise fallback replace. Order: cover, contents,
    section1..section7, appendices. Missing or None values render as empty.
    """
    parts: List[str] = []
    values = values or {}
    use_jinja = _JINJA_AVAILABLE

    # Cover
    if "cover" in template and isinstance(template["cover"], dict):
        text = template["cover"].get("fixed_text") or ""
        block_vals = values.get("cover") or {}
        if use_jinja:
            try:
                text = _render_block_jinja(text, block_vals)
            except Exception:
                text = _render_block_fallback(text, block_vals)
        else:
            text = _render_block_fallback(text, block_vals)
        parts.append(text)

    # Contents (no user_fields; append as-is or minimal render)
    if "contents" in template and isinstance(template["contents"], dict):
        parts.append(template["contents"].get("fixed_text") or "")

    # Sections 1–7
    for i in range(1, 8):
        sk = f"section{i}"
        if sk not in template or not isinstance(template[sk], dict):
            continue
        keys_sorted = sorted(template[sk].keys(), key=_section_sort_key)
        for sub_key in keys_sorted:
            block = template[sk][sub_key]
            if not isinstance(block, dict) or "fixed_text" not in block:
                continue
            text = block.get("fixed_text") or ""
            block_vals = (values.get(sk) or {}).get(sub_key) or {}
            if use_jinja:
                try:
                    text = _render_block_jinja(text, block_vals)
                except Exception:
                    text = _render_block_fallback(text, block_vals)
            else:
                text = _render_block_fallback(text, block_vals)
            parts.append(text)

    # Appendices
    if "appendices" in template and isinstance(template["appendices"], dict):
        for app_key in sorted(template["appendices"].keys(), key=_section_sort_key):
            block = template["appendices"][app_key]
            if not isinstance(block, dict) or "fixed_text" not in block:
                continue
            text = block.get("fixed_text") or ""
            block_vals = (values.get("appendices") or {}).get(app_key) or {}
            if use_jinja:
                try:
                    text = _render_block_jinja(text, block_vals)
                except Exception:
                    text = _render_block_fallback(text, block_vals)
            else:
                text = _render_block_fallback(text, block_vals)
            parts.append(text)

    return "\n\n".join(p for p in parts if p is not None and len(str(p).strip()) > 0)


def serialize_value(val: Any) -> Any:
    """Convert date/datetime to string for JSON/serialization."""
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return val


def is_template_ready() -> bool:
    """Return True if template file exists and is loadable (for UI guards)."""
    try:
        load_ev_pdd_template()
        return True
    except (FileNotFoundError, ValueError):
        return False
