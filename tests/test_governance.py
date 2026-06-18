# SPDX-License-Identifier: Apache-2.0
import json
from ati_audit.scorers.base import grounded_score, FLOOR


def test_floor_caps_when_artifact_missing(fake_llm):
    llm = fake_llm([json.dumps({"score": 9, "rationale": "great", "evidence": []})])
    r = grounded_score("G8", llm, "", "rubric", required_present=False, applicable=True)
    assert r.score <= FLOOR
    assert r.active is True


def test_uses_llm_score_when_grounded(fake_llm):
    llm = fake_llm([json.dumps({
        "score": 8, "rationale": "policy found",
        "evidence": [{"category": "policy", "snippet": "AI policy v1", "source": "AI_POLICY.md"}]
    })])
    r = grounded_score("G8", llm, "AI policy v1", "rubric", required_present=True, applicable=True)
    assert r.score == 8
    assert r.evidence[0].category == "policy"


def test_score_governance_floors_without_evidence(fake_llm):
    """No evidence collected → universal governance directions are floored even if the LLM
    returns a high score (honest-defaults guard, not benefit of the doubt)."""
    from ati_audit.scorers.governance import score_governance
    from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg
    cfg = AuditConfig(Project("Acme", False, ""), Sources(), ModelCfg(), LLMCfg(), SubmitCfg())
    high = json.dumps({"score": 10, "rationale": "looks great", "evidence": []})
    llm = fake_llm([high] * 5)  # G1, G2, G3, G4, G7 (AI codes excluded when has_ai=False)
    results = score_governance(cfg, {}, {"files": {}, "found": {}}, llm)
    scored = [r for r in results if r.active and r.applicable]
    assert scored, "expected universal directions to be scored"
    assert all(r.score <= FLOOR for r in scored), [(r.code, r.score) for r in scored]


# ---------------------------------------------------------------------------
# G9 jurisdiction-aware tests
# ---------------------------------------------------------------------------

def test_load_jurisdictions():
    """Registry loads correctly and KZ entry has required fields."""
    from ati_audit.jurisdictions import load_jurisdictions
    j = load_jurisdictions()
    assert "KZ" in j
    assert "law" in j["KZ"]
    assert isinstance(j["KZ"]["requirements"], list)
    assert len(j["KZ"]["requirements"]) > 0


def test_g9_uses_country_law(fake_llm):
    """G9 with country=KZ references Kazakhstan law in the rationale."""
    from ati_audit.scorers.governance import score_governance
    from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg
    # has_ai=True, country=KZ, with consent evidence present (so G9 is not floored)
    cfg = AuditConfig(
        Project("Acme", True, "", "KZ"), Sources(), ModelCfg(), LLMCfg(), SubmitCfg()
    )
    site_ev = {"has_consent": True, "has_ai_disclosure": True, "has_privacy_policy": True}
    docs_ev = {"files": {}, "found": {}}
    llm_response = json.dumps({"score": 7, "rationale": "consent found", "evidence": []})
    # All 8 codes are scored when has_ai=True: G1,G2,G3,G4,G7,G8,G9,G10
    llm = fake_llm([llm_response] * 8)
    results = score_governance(cfg, site_ev, docs_ev, llm)
    g9 = next(r for r in results if r.code == "G9")
    assert g9.applicable is True
    assert g9.score == 7
    # Rationale must mention the Kazakhstan law label
    assert "230-VIII" in g9.rationale or "Kazakhstan" in g9.rationale


def test_g9_unknown_country_flagged(fake_llm):
    """G9 with an unknown country code flags 'general assessment' in the rationale."""
    from ati_audit.scorers.governance import score_governance
    from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg
    cfg = AuditConfig(
        Project("Acme", True, "", "ZZ"), Sources(), ModelCfg(), LLMCfg(), SubmitCfg()
    )
    site_ev = {"has_consent": True, "has_ai_disclosure": False, "has_privacy_policy": False}
    docs_ev = {"files": {}, "found": {}}
    llm_response = json.dumps({"score": 5, "rationale": "partial", "evidence": []})
    llm = fake_llm([llm_response] * 8)
    results = score_governance(cfg, site_ev, docs_ev, llm)
    g9 = next(r for r in results if r.code == "G9")
    assert "general assessment" in g9.rationale or "not in registry" in g9.rationale
