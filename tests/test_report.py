# SPDX-License-Identifier: Apache-2.0
from ati_audit.report import build_report, to_html
from ati_audit.models import ScoreResult
from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg


def _cfg(has_ai):
    return AuditConfig(Project("Acme", has_ai, ""), Sources(), ModelCfg(), LLMCfg(), SubmitCfg())


def test_report_has_index_and_names():
    rep = build_report(
        _cfg(False),
        [ScoreResult("G1", 8, True, True, "ok", []),
         ScoreResult("G8", None, False, False, "n/a", [])]
    )
    assert rep["index"] == 8.0
    g1 = next(d for d in rep["directions"] if d["code"] == "G1")
    assert g1["name"] == "Systems registry"
    assert "<html" in to_html(rep).lower()
