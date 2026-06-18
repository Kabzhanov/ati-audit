# SPDX-License-Identifier: Apache-2.0
from ati_audit.models import ScoreResult, Evidence
from ati_audit.aggregate import compute_index


def _r(code, score, active=True, applicable=True):
    return ScoreResult(code, score, active, applicable, "", [])


def test_index_is_mean_of_active_applicable():
    rs = [_r("G1", 8), _r("G2", 6), _r("G6", None, active=False)]  # G6 inactive ignored
    assert compute_index(rs) == 7.0


def test_non_ai_project_excludes_ai_directions():
    rs = [_r("G1", 7), _r("G2", 7), _r("G8", 2, applicable=False)]  # G8 N/A excluded
    assert compute_index(rs) == 7.0


def test_no_active_returns_zero():
    assert compute_index([_r("G8", None, active=False, applicable=False)]) == 0.0
