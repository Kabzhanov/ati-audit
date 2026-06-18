# SPDX-License-Identifier: Apache-2.0
from ati_audit.cli import run_audit
from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg


def test_run_audit_non_ai_excludes_ai_dirs(tmp_path, fake_llm, fake_connector):
    cfg = AuditConfig(
        Project("Acme", False, ""), Sources(docs_path=str(tmp_path)),
        ModelCfg(), LLMCfg(), SubmitCfg()
    )
    # 5 governance LLM calls (G1,G2,G3,G4,G7) + G5 => supply enough JSON responses
    resp = ['{"score": 7, "rationale": "x", "evidence": []}'] * 6
    rep = run_audit(cfg, llm=fake_llm(resp), connector=fake_connector([]), reviews=[])
    codes = {d["code"]: d for d in rep["directions"]}
    assert codes["G8"]["applicable"] is False and codes["G11"]["applicable"] is False
    assert codes["G1"]["score"] == 7
    assert rep["index"] > 0
