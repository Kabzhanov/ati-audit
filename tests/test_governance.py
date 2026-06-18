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
