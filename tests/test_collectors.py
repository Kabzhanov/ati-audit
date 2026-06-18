# SPDX-License-Identifier: Apache-2.0
from ati_audit.collectors.site import fetch_site
from ati_audit.collectors.docs import scan_docs


def test_site_detects_ai_disclosure():
    html = '<div>Online · Вам отвечает ИИ</div><a href="/privacy-policy">privacy</a>'
    ev = fetch_site("http://x", _get=lambda u: html)
    assert ev["has_ai_disclosure"] is True
    assert ev["has_privacy_policy"] is True
    assert "html" not in ev


def test_site_no_html_in_result():
    """fetch_site must not return the raw html key."""
    ev = fetch_site("https://x", _get=lambda u: "some html content")
    assert "html" not in ev


def test_site_rejects_non_http_scheme():
    """Non-http/https URLs must return all-False without fetching."""
    called = []
    ev = fetch_site("ftp://evil.example.com", _get=lambda u: called.append(u) or "")
    assert ev == {"has_ai_disclosure": False, "has_consent": False, "has_privacy_policy": False}
    assert called == []


def test_site_rejects_empty_url():
    """Empty URL must return all-False without fetching."""
    called = []
    ev = fetch_site("", _get=lambda u: called.append(u) or "")
    assert ev == {"has_ai_disclosure": False, "has_consent": False, "has_privacy_policy": False}
    assert called == []


def test_docs_scan_finds_policy(tmp_path):
    (tmp_path / "AI_POLICY.md").write_text("# AI usage policy\nprinciples")
    out = scan_docs(str(tmp_path))
    assert out["found"]["policy"] is True
    assert "AI_POLICY.md" in out["files"]
