"""
Semantic + guardrail methodology matcher with deterministic fallback.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ai_workflow.methodology_corpus import (
    corpus_hash,
    get_methodology_cards,
    load_cached_embeddings,
    save_cached_embeddings,
)
from ai_workflow.project_intelligence import build_project_intelligence

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    genai = None
    GEMINI_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None
    SKLEARN_AVAILABLE = False


@dataclass
class MethodologyRecommendation:
    """Recommendation object with legacy and extended UI fields."""
    methodology_id: str
    title: str
    category: str
    confidence: float
    reasons: List[str] = field(default_factory=list)
    final_score: float = 0.0
    confidence_pct: float = 0.0
    why_matches: List[str] = field(default_factory=list)
    eligibility_checks: List[Dict[str, str]] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def code(self) -> str:
        return self.methodology_id

    @property
    def name(self) -> str:
        return self.title


class MethodologyMatcher:
    """Default recommendation engine: semantic retrieval + guardrails + optional rerank."""

    METHODOLOGY_KEYWORDS = {
        "VM0038": ["ev", "electric vehicle", "charging", "charger", "evse", "transport electrification"],
        "VM0047": ["afforestation", "reforestation", "tree planting", "forest restoration"],
        "VM0048": ["redd", "avoided deforestation", "deforestation", "forest degradation"],
        "VM0033": ["wetland", "mangrove", "tidal wetland", "seagrass", "blue carbon"],
        "VM0042": ["agriculture", "soil", "cropland", "land management", "cover crop"],
        "VM0044": ["biochar", "pyrolysis", "biomass char"],
        "AMS-III.E": ["organic waste", "landfill", "composting", "methane avoidance"],
        "VMR0006": ["cookstove", "clean cooking", "household stove", "biomass stove"],
        "AMS-I.D": ["grid connected", "renewable electricity", "solar", "wind", "hydro"],
        "VM0043": ["concrete", "cement", "co2 utilization", "mineralization"],
    }

    def __init__(
        self,
        methodology_database: Dict[str, Dict[str, Any]],
        api_key: Optional[str] = None,
        enable_llm_rerank: Optional[bool] = None,
        enable_embeddings: Optional[bool] = None,
        fallback_mode: Optional[str] = None,
    ):
        self.methodology_db = methodology_database
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.enable_llm_rerank = (
            bool(self.api_key and GEMINI_AVAILABLE) if enable_llm_rerank is None else bool(enable_llm_rerank)
        )
        self.enable_embeddings = True if enable_embeddings is None else bool(enable_embeddings)
        self.fallback_mode = fallback_mode or "semantic_local"
        self._gemini_model = None

        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception:
                self._gemini_model = None

        self.last_project_intelligence: Dict[str, Any] = {}

    def recommend(
        self,
        project_description: str,
        top_k: int = 3,
        extracted_context: Optional[Dict[str, Any]] = None,
        enable_llm_rerank: Optional[bool] = None,
        enable_embeddings: Optional[bool] = None,
    ) -> List[MethodologyRecommendation]:
        """
        Return methodology recommendations with explainability details.
        """
        description = (project_description or "").strip()
        context = extracted_context or {}
        if len(description) < 10:
            return self._legacy_keyword_recommend(description, top_k)

        llm_for_intelligence = self._gemini_model if self._gemini_model is not None else None
        project_intelligence = build_project_intelligence(description, context, llm=llm_for_intelligence)
        self.last_project_intelligence = project_intelligence

        cards = get_methodology_cards()
        scores = self._semantic_scores(
            project_intelligence,
            cards,
            use_embeddings=self.enable_embeddings if enable_embeddings is None else bool(enable_embeddings),
        )

        candidates = []
        for card in cards:
            code = card["code"]
            semantic_score = scores.get(code, 0.0)
            guarded_score, checks, why, assumptions = self._apply_guardrails(
                project_intelligence, card, semantic_score, description
            )
            candidates.append(
                {
                    "code": code,
                    "name": card["name"],
                    "category": card["category"],
                    "semantic_score": semantic_score,
                    "final_score": guarded_score,
                    "why_matches": why,
                    "eligibility_checks": checks,
                    "assumptions": assumptions,
                    "metadata": card["metadata"],
                }
            )

        candidates.sort(key=lambda x: (x["final_score"], x["semantic_score"], x["code"]), reverse=True)

        do_rerank = self.enable_llm_rerank if enable_llm_rerank is None else bool(enable_llm_rerank)
        if do_rerank and self._gemini_model is not None:
            reranked = self._rerank_with_llm(project_intelligence, candidates[:5])
            if reranked:
                by_code = {c["code"]: c for c in candidates}
                for rank_item in reranked:
                    code = rank_item.get("code")
                    if code in by_code:
                        llm_score = _clamp(float(rank_item.get("score", 0.0)), 0.0, 1.0)
                        by_code[code]["final_score"] = _clamp(
                            by_code[code]["final_score"] * 0.7 + llm_score * 0.3, 0.0, 1.0
                        )
                        llm_why = rank_item.get("why_matches") or []
                        llm_assume = rank_item.get("assumptions") or []
                        by_code[code]["why_matches"] = _merge_unique(by_code[code]["why_matches"], llm_why)
                        by_code[code]["assumptions"] = _merge_unique(by_code[code]["assumptions"], llm_assume)
                candidates = sorted(candidates, key=lambda x: (x["final_score"], x["code"]), reverse=True)

        recommendations: List[MethodologyRecommendation] = []
        for item in candidates[:top_k]:
            pct = round(item["final_score"] * 100, 1)
            recommendations.append(
                MethodologyRecommendation(
                    methodology_id=item["code"],
                    title=item["name"],
                    category=item["category"],
                    confidence=pct,
                    reasons=item["why_matches"][:3],
                    final_score=item["final_score"],
                    confidence_pct=pct,
                    why_matches=item["why_matches"][:5],
                    eligibility_checks=item["eligibility_checks"],
                    assumptions=item["assumptions"][:6],
                    metadata=item["metadata"],
                )
            )

        if not recommendations:
            return self._legacy_keyword_recommend(description, top_k)
        return recommendations

    def _semantic_scores(
        self,
        project_intelligence: Dict[str, Any],
        cards: List[Dict[str, Any]],
        use_embeddings: bool,
    ) -> Dict[str, float]:
        """Compute semantic similarity scores using embeddings or local TF-IDF."""
        query = self._query_text(project_intelligence)
        docs = [c["card_text"] for c in cards]
        codes = [c["code"] for c in cards]

        if use_embeddings and self.api_key and GEMINI_AVAILABLE:
            scores = self._gemini_embedding_scores(query, cards)
            if scores:
                return scores

        if SKLEARN_AVAILABLE:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            matrix = vectorizer.fit_transform([query] + docs)
            sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
            return {code: _clamp(float(score), 0.0, 1.0) for code, score in zip(codes, sims)}

        # Last-resort deterministic lexical overlap fallback
        query_tokens = set(query.lower().split())
        scores = {}
        for code, doc in zip(codes, docs):
            doc_tokens = set(doc.lower().split())
            union = len(query_tokens | doc_tokens) or 1
            scores[code] = len(query_tokens & doc_tokens) / union
        return scores

    def _gemini_embedding_scores(self, query: str, cards: List[Dict[str, Any]]) -> Dict[str, float]:
        """Gemini embedding path with cache fallback."""
        try:
            version = corpus_hash(cards)
            cached = load_cached_embeddings(version, "gemini-text-embedding-004")
            if cached is None:
                card_texts = [c["card_text"] for c in cards]
                emb = genai.embed_content(
                    model="models/text-embedding-004",
                    content=card_texts,
                    task_type="retrieval_document",
                )
                vectors = emb.get("embedding") or emb.get("embeddings") or []
                if vectors and isinstance(vectors[0], dict):
                    vectors = [v.get("values", []) for v in vectors]
                card_embeddings = {
                    c["code"]: vectors[idx]
                    for idx, c in enumerate(cards)
                    if idx < len(vectors)
                }
                if card_embeddings:
                    save_cached_embeddings(version, "gemini-text-embedding-004", card_embeddings)
            else:
                card_embeddings = cached

            if not card_embeddings:
                return {}

            query_emb = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query",
            )
            qvec = query_emb.get("embedding")
            if isinstance(qvec, dict):
                qvec = qvec.get("values")
            if not qvec:
                return {}

            scores: Dict[str, float] = {}
            for code, cvec in card_embeddings.items():
                sim = _cosine(qvec, cvec)
                scores[code] = _clamp((sim + 1.0) / 2.0, 0.0, 1.0)
            return scores
        except Exception:
            return {}

    def _apply_guardrails(
        self,
        project_intelligence: Dict[str, Any],
        card: Dict[str, Any],
        semantic_score: float,
        description: str,
    ) -> Tuple[float, List[Dict[str, str]], List[str], List[str]]:
        """Apply deterministic eligibility and fit checks with penalties."""
        metadata = card.get("metadata", {})
        checks: List[Dict[str, str]] = []
        why: List[str] = []
        assumptions: List[str] = list(project_intelligence.get("assumptions", []))
        penalty = 0.0
        bonus = 0.0

        project_sector = project_intelligence.get("sector")
        card_sector = metadata.get("sector")
        sector_status = "unknown"
        if project_sector and card_sector:
            if project_sector == card_sector:
                sector_status = "pass"
                why.append(f"Sector fit: {project_sector}")
                bonus += 0.12
            else:
                sector_status = "fail"
                penalty += 0.35
        checks.append(
            {
                "check": "Sector/category alignment",
                "status": sector_status,
                "note": f"Project sector={project_sector}, methodology sector={card_sector}",
            }
        )
        if sector_status == "unknown":
            assumptions.append("Sector alignment could not be fully verified.")

        project_mechanism = project_intelligence.get("mechanism")
        card_mechanism = metadata.get("mechanism")
        mech_status = "unknown"
        if project_mechanism and card_mechanism:
            if project_mechanism == card_mechanism:
                mech_status = "pass"
                why.append(f"Mechanism fit: {project_mechanism}")
                bonus += 0.08
            else:
                mech_status = "fail"
                penalty += 0.15
        checks.append(
            {
                "check": "Mechanism alignment",
                "status": mech_status,
                "note": f"Project mechanism={project_mechanism}, methodology mechanism={card_mechanism}",
            }
        )

        grid_required = bool(metadata.get("grid_connected_required"))
        grid_connected = project_intelligence.get("grid_connected")
        grid_status = "pass"
        grid_note = "No grid-connection requirement"
        if grid_required:
            if grid_connected is True:
                grid_status = "pass"
                grid_note = "Methodology requires grid connection and project indicates grid connectivity"
                why.append("Grid-connection requirement appears satisfied")
                bonus += 0.07
            elif grid_connected is False:
                grid_status = "fail"
                grid_note = "Methodology requires grid connection, but project appears off-grid"
                penalty += 0.35
            else:
                grid_status = "unknown"
                grid_note = "Methodology requires grid connection, but project signal is unclear"
                assumptions.append("Grid connectivity was not explicit in project description.")
        checks.append({"check": "Grid connection requirement", "status": grid_status, "note": grid_note})

        metering_required = bool(metadata.get("requires_metering"))
        metering_available = (project_intelligence.get("data_availability") or {}).get("metering")
        metering_status = "pass"
        metering_note = "No strict metering requirement detected"
        if metering_required:
            if metering_available is True:
                metering_status = "pass"
                metering_note = "Required metering appears available"
                why.append("Monitoring requirement aligns with available metering")
                bonus += 0.06
            elif metering_available is False:
                metering_status = "fail"
                metering_note = "Methodology requires metering but availability appears absent"
                penalty += 0.25
            else:
                metering_status = "unknown"
                metering_note = "Methodology requires metering; data availability is unclear"
                assumptions.append("Metering availability should be verified.")
        checks.append({"check": "Monitoring data fit", "status": metering_status, "note": metering_note})

        disqualifiers = metadata.get("disqualifier_keywords") or []
        disq_status = "pass"
        disq_note = "No explicit disqualifier found"
        desc_lower = (description or "").lower()
        for term in disqualifiers:
            if term in desc_lower:
                disq_status = "fail"
                disq_note = f"Disqualifier detected: {term}"
                penalty += 0.4
                break
        checks.append({"check": "Known disqualifiers", "status": disq_status, "note": disq_note})

        summary = project_intelligence.get("summary")
        if summary:
            why.append("Semantic similarity based on project summary and methodology applicability")
        if metadata.get("eligibility"):
            why.append(f"Eligibility overlap considered from {card['code']} card")

        final_score = _clamp(semantic_score + bonus - penalty, 0.0, 1.0)
        return final_score, checks, _merge_unique(why, []), _merge_unique(assumptions, [])

    def _rerank_with_llm(
        self,
        project_intelligence: Dict[str, Any],
        top_candidates: List[Dict[str, Any]],
    ) -> Optional[List[Dict[str, Any]]]:
        """Optional final rerank grounded only in methodology cards."""
        if not top_candidates or self._gemini_model is None:
            return None
        prompt = {
            "task": "Re-rank methodologies using only provided project intelligence and methodology cards.",
            "rules": [
                "Do not use outside knowledge.",
                "Return only valid JSON array.",
                "Each item must include: code, score(0..1), why_matches(list), assumptions(list).",
            ],
            "project_intelligence": project_intelligence,
            "candidates": [
                {
                    "code": c["code"],
                    "name": c["name"],
                    "category": c["category"],
                    "metadata": c["metadata"],
                    "current_score": c["final_score"],
                    "why_matches": c["why_matches"],
                }
                for c in top_candidates
            ],
        }
        try:
            response = self._gemini_model.generate_content(json.dumps(prompt, ensure_ascii=True))
            text = getattr(response, "text", "").strip()
            cleaned = _strip_fences(text)
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                output = []
                for item in parsed:
                    if not isinstance(item, dict):
                        continue
                    code = str(item.get("code", "")).strip()
                    if not code:
                        continue
                    output.append(
                        {
                            "code": code,
                            "score": _clamp(float(item.get("score", 0.0)), 0.0, 1.0),
                            "why_matches": [str(x) for x in item.get("why_matches", []) if str(x).strip()],
                            "assumptions": [str(x) for x in item.get("assumptions", []) if str(x).strip()],
                        }
                    )
                return output
        except Exception:
            return None
        return None

    def _query_text(self, project_intelligence: Dict[str, Any]) -> str:
        data = project_intelligence
        availability = data.get("data_availability", {}) or {}
        parts = [
            f"Summary: {data.get('summary', '')}",
            f"Sector: {data.get('sector', '')}",
            f"Project Type: {data.get('project_type', '')}",
            f"Mechanism: {data.get('mechanism', '')}",
            f"GHG Sources: {' '.join(data.get('ghg_sources', []))}",
            f"Grid Connected: {data.get('grid_connected')}",
            f"New Build: {data.get('new_build')}",
            f"Metering: {availability.get('metering')}",
            f"Fuel Records: {availability.get('fuel_use_records')}",
            f"Baseline Data: {availability.get('baseline_data')}",
            f"Constraints: {' '.join(data.get('constraints', []))}",
        ]
        return "\n".join(parts)

    def _legacy_keyword_recommend(self, project_description: str, top_k: int = 3) -> List[MethodologyRecommendation]:
        """Legacy deterministic keyword fallback path."""
        desc_lower = (project_description or "").lower()
        scores: Dict[str, float] = {}
        match_details: Dict[str, List[str]] = {}

        for method_id, keywords in self.METHODOLOGY_KEYWORDS.items():
            matched = [kw for kw in keywords if kw in desc_lower]
            if matched:
                score = min(1.0, len(matched) / max(1, len(keywords)) + 0.35)
                scores[method_id] = score
                match_details[method_id] = matched

        if not scores:
            defaults = ["VM0038", "AMS-I.D", "VM0047", "VM0048", "VM0042"]
            scores = {mid: 0.5 for mid in defaults if mid in self.methodology_db}
            match_details = {mid: ["Default deterministic fallback"] for mid in scores}

        sorted_methods = sorted(scores.items(), key=lambda x: (x[1], x[0]), reverse=True)
        recommendations: List[MethodologyRecommendation] = []
        for method_id, score in sorted_methods[:top_k]:
            method = self.methodology_db.get(method_id)
            if not method:
                continue
            pct = round(score * 100, 1)
            reasons = [f"Matched concept: {kw}" for kw in match_details.get(method_id, [])[:3]]
            recommendations.append(
                MethodologyRecommendation(
                    methodology_id=method_id,
                    title=method.get("title", method_id),
                    category=method.get("category", "Unknown"),
                    confidence=pct,
                    reasons=reasons,
                    final_score=score,
                    confidence_pct=pct,
                    why_matches=reasons,
                    eligibility_checks=[],
                    assumptions=["Used keyword fallback mode."],
                    metadata={},
                )
            )
        return recommendations


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _merge_unique(left: List[str], right: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in list(left or []) + list(right or []):
        text = str(item).strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _strip_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return cleaned
