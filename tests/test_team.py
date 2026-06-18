# SPDX-License-Identifier: Apache-2.0
import json
from ati_audit.scorers.team import score_team
from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg


def _cfg(cred_path):
    return AuditConfig(
        Project("Acme", True, ""), Sources(credentials_path=cred_path),
        ModelCfg(), LLMCfg(), SubmitCfg()
    )


def test_floored_when_no_documents(tmp_path, fake_llm):
    r = score_team(_cfg(str(tmp_path)), fake_llm(['{"score": 9, "level": "x", "rationale": "y"}']))
    assert r.code == "G5" and r.score <= 3
    assert "self-reported" in r.rationale.lower()


def test_scores_from_credential_text(tmp_path, fake_llm):
    (tmp_path / "diploma.txt").write_text("Red diploma, CS teacher, 10y experience")
    r = score_team(
        _cfg(str(tmp_path)),
        fake_llm(['{"score": 8, "level": "formal_education", "rationale": "ok"}'])
    )
    assert r.score == 8 and r.applicable is True
