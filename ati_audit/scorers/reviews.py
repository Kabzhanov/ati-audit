# SPDX-License-Identifier: Apache-2.0
from ati_audit.models import ScoreResult


def score_reviews(reviews: list[dict]) -> ScoreResult:
    valid = [r for r in reviews if isinstance(r.get("stars"), (int, float))]
    if len(valid) < 3:
        return ScoreResult(
            "G6", None, active=False, applicable=True,
            rationale=f"{len(valid)} reviews (<3) → module inactive", evidence=[]
        )
    score = round(sum(r["stars"] for r in valid) / len(valid) * 2)
    return ScoreResult(
        "G6", score, active=True, applicable=True,
        rationale=f"{len(valid)} reviews, avg→{score}/10", evidence=[]
    )
