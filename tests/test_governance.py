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
