# SPDX-License-Identifier: Apache-2.0
import json
from ati_audit.models import ScoreResult, Evidence

FLOOR = 3
_PROMPT = (
    "You score an IT/AI governance direction 1-10 strictly from the EVIDENCE below. "
    "If evidence is absent, score low. Return ONLY JSON: "
    '{{"score": int, "rationale": str, "evidence": [{{"category": str, "snippet": str, "source": str}}]}}.'
    "\n\nRUBRIC:\n{rubric}\n\nEVIDENCE:\n{evidence}"
)


def grounded_score(
    code, llm, evidence_text, rubric, *, required_present: bool, applicable: bool
) -> ScoreResult:
    raw = llm.complete(_PROMPT.format(rubric=rubric, evidence=evidence_text or "(none)"))
    try:
        d = json.loads(raw)
        score = int(d.get("score", FLOOR))
        ev = [
            Evidence(e.get("category", ""), e.get("snippet", ""), e.get("source", ""))
            for e in d.get("evidence", [])
        ]
        rationale = str(d.get("rationale", ""))
    except (ValueError, TypeError):
        score, ev, rationale = FLOOR, [], "unparseable LLM output; floored"
    if not required_present:
        score = min(score, FLOOR)
        rationale = "required artifact not found → floored. " + rationale
    return ScoreResult(code, score, active=True, applicable=applicable, rationale=rationale, evidence=ev)
