# SPDX-License-Identifier: Apache-2.0
import json
from ati_audit.models import ScoreResult, Evidence
from ati_audit.collectors.credentials import read_credentials

FLOOR = 3
_RUBRIC = (
    'Score IT-team verification 1-10 from credential text. Levels: formal_education > '
    'certification > portfolio. Return ONLY JSON {"score": int, "level": str, "rationale": str}.'
)


def score_team(cfg, llm) -> ScoreResult:
    docs = read_credentials(cfg.sources.credentials_path)
    note = "self-reported (not registry-verified). "
    if not docs:
        return ScoreResult(
            "G5", FLOOR, True, True,
            note + "no credential documents found → floored", []
        )
    blob = "\n\n".join(f"[{d['file']}]\n{d['text']}" for d in docs)
    try:
        d = json.loads(llm.complete(_RUBRIC + "\n\n" + blob))
        score = int(d.get("score", FLOOR))
        rat = note + str(d.get("rationale", ""))
    except (ValueError, TypeError):
        score, rat = FLOOR, note + "unparseable LLM output; floored"
    ev = [Evidence("credential", d["file"], d["file"]) for d in docs]  # filename only, no PII text
    return ScoreResult("G5", score, True, True, rat, ev)
