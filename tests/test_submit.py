# SPDX-License-Identifier: Apache-2.0
from ati_audit.submit import build_payload, submit


def test_payload_excludes_raw_evidence_and_pii():
    report = {
        "index": 7.0,
        "project": {"name": "Acme", "site_url": "https://acme.test"},
        "directions": [{
            "code": "G1", "score": 7, "active": True, "applicable": True,
            "rationale": "contact ivan@acme.test found", "evidence_categories": ["registry"]
        }],
        "generated_at": "now",
    }
    p = build_payload(report)
    d = p["directions"][0]
    assert "ivan@acme.test" not in d["rationale_redacted"]
    assert "evidence" not in d and "html" not in str(p)
    assert "rationale" not in d  # only rationale_redacted leaves


def test_submit_posts_payload():
    captured = {}

    def _post(url, json):
        captured["url"] = url
        captured["json"] = json
        return {"ok": True}

    out = submit({"index": 7.0}, "https://reg.test/api", _post=_post)
    assert out["ok"] and captured["url"].endswith("/api")
