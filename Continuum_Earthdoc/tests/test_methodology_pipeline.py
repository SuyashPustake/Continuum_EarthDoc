import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.pdd_agent import METHODOLOGY_DATABASE
from ai_workflow.methodology_matcher import MethodologyMatcher
from ai_workflow.project_intelligence import build_project_intelligence


def test_project_intelligence_heuristic_required_keys():
    description = (
        "We will install electric vehicle charging stations with revenue-grade metering "
        "to support EV adoption and reduce fossil fuel use."
    )
    context = {"project_type": "Electric Vehicle Charging Infrastructure", "category": "Transport"}
    result = build_project_intelligence(description, context, llm=None)

    assert isinstance(result, dict)
    assert "summary" in result
    assert "sector" in result
    assert "project_type" in result
    assert "mechanism" in result
    assert "ghg_sources" in result
    assert "data_availability" in result
    assert set(result["data_availability"].keys()) == {"metering", "fuel_use_records", "baseline_data"}
    assert "confidence" in result
    assert set(result["confidence"].keys()) == {"sector", "project_type", "mechanism"}


def test_semantic_ranking_stable_for_ev_description():
    matcher = MethodologyMatcher(
        METHODOLOGY_DATABASE,
        api_key=None,
        enable_llm_rerank=False,
        enable_embeddings=False,
        fallback_mode="semantic_local",
    )
    description = (
        "The project develops grid connected EV charging infrastructure with revenue-grade "
        "metering and expected emissions reduction from replacing gasoline vehicles."
    )
    context = {"project_type": "Electric Vehicle Charging Infrastructure", "category": "Transport"}
    recs = matcher.recommend(description, top_k=3, extracted_context=context, enable_llm_rerank=False, enable_embeddings=False)

    assert len(recs) == 3
    assert recs[0].methodology_id == "VM0038"
    assert recs[0].final_score >= recs[1].final_score >= recs[2].final_score


def test_guardrail_sector_mismatch_penalty():
    matcher = MethodologyMatcher(
        METHODOLOGY_DATABASE,
        api_key=None,
        enable_llm_rerank=False,
        enable_embeddings=False,
        fallback_mode="semantic_local",
    )
    card = {
        "code": "AMS-I.D",
        "name": "Grid Connected Renewable Electricity Generation",
        "category": "Energy",
        "card_text": "renewable grid electricity generation",
        "metadata": {
            "sector": "Energy",
            "mechanism": "emission_reduction",
            "grid_connected_required": True,
            "requires_metering": True,
            "eligibility": [],
            "exclusions": [],
            "disqualifier_keywords": [],
        },
    }
    project_intelligence = {
        "summary": "Forest restoration project with sequestration benefits.",
        "sector": "AFOLU",
        "mechanism": "removal",
        "grid_connected": False,
        "data_availability": {"metering": False},
        "assumptions": [],
    }
    final_score, checks, _, _ = matcher._apply_guardrails(
        project_intelligence=project_intelligence,
        card=card,
        semantic_score=0.9,
        description="forest restoration with no power export",
    )

    assert final_score < 0.6
    status_by_check = {item["check"]: item["status"] for item in checks}
    assert status_by_check["Sector/category alignment"] == "fail"
