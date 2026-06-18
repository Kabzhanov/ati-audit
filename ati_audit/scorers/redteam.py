# SPDX-License-Identifier: Apache-2.0
from ati_audit.models import ScoreResult, Evidence
from ati_audit.probing import load_probes, run_probes, resistance_rate


def score_redteam(cfg, connector, llm) -> ScoreResult:
    applicable = bool(cfg.project.has_ai)
    if not applicable:
        return ScoreResult("G11", None, False, False, "not applicable (no AI in project)", [])
    results = run_probes(connector, llm, load_probes())
    rate = resistance_rate(results)
    score = round(rate * 9) + 1
    fails = [r for r in results if not r.passed]
    ev = [Evidence(r.category, f"failed probe {r.id}", "redteam") for r in fails]
    return ScoreResult(
        "G11", score, True, True,
        f"resistance {rate:.0%} over {len(results)} probes; {len(fails)} failed",
        ev,
    )
