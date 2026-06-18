# SPDX-License-Identifier: Apache-2.0
from ati_audit.scorers.reviews import score_reviews


def test_inactive_below_three_reviews():
    r = score_reviews([{"stars": 5}, {"stars": 4}])
    assert r.code == "G6" and r.active is False and r.score is None


def test_active_score_is_mean_times_two():
    r = score_reviews([{"stars": 5}, {"stars": 4}, {"stars": 5}])  # mean 4.67 -> 9
    assert r.active is True and r.score == 9
