# SPDX-License-Identifier: Apache-2.0
from ati_audit.models import ScoreResult


def compute_index(results: list[ScoreResult]) -> float:
    scores = [r.score for r in results if r.active and r.applicable and r.score is not None]
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 1)
