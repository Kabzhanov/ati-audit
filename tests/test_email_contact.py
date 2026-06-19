# SPDX-License-Identifier: Apache-2.0
"""Tests for the official-contact email trust signal.

Covers:
- Corporate vs free-provider email detection
- MX seam injection (no real DNS)
- G1 _required() lifted by corporate/MX-verified email
- _evidence_text() surfaces the email signal
- fetch_site() includes email keys in returned dict
"""
import json

from ati_audit.collectors.site import (
    _extract_emails,
    _is_corporate,
    mx_ok,
    find_corporate_emails,
    fetch_site,
)
from ati_audit.scorers.governance import _required, _evidence_text


# ---------------------------------------------------------------------------
# _extract_emails
# ---------------------------------------------------------------------------

def test_extract_emails_simple():
    html = "<p>Contact us at info@example.kz for details.</p>"
    assert "info@example.kz" in _extract_emails(html)


def test_extract_emails_multiple():
    html = "<p>a@corp.kz and b@corp.kz and c@gmail.com</p>"
    emails = _extract_emails(html)
    assert "a@corp.kz" in emails
    assert "c@gmail.com" in emails


def test_extract_emails_empty():
    assert _extract_emails("no email here") == []


def test_extract_emails_lowercased():
    emails = _extract_emails("<a>CEO@CORP.KZ</a>")
    assert "ceo@corp.kz" in emails
    assert all(e == e.lower() for e in emails)


def test_extract_emails_deduped():
    html = "<p>ceo@corp.kz CEO@CORP.KZ ceo@corp.kz</p>"
    emails = _extract_emails(html)
    assert emails.count("ceo@corp.kz") == 1


# ---------------------------------------------------------------------------
# _is_corporate / free-provider exclusion
# ---------------------------------------------------------------------------

def test_free_providers_excluded():
    free = [
        "user@gmail.com", "user@googlemail.com", "user@mail.ru", "user@inbox.ru",
        "user@yandex.ru", "user@yandex.kz", "user@ya.ru",
        "user@outlook.com", "user@hotmail.com", "user@live.com",
        "user@yahoo.com", "user@yahoo.co.uk",
        "user@icloud.com", "user@me.com",
        "user@proton.me", "user@protonmail.com",
        "user@gmx.com", "user@aol.com", "user@zoho.com",
    ]
    for email in free:
        assert not _is_corporate(email), f"Expected free: {email}"


def test_corporate_emails_detected():
    corporate = [
        "ceo@acme.kz",
        "info@corp.company",
        "support@example.co.uk",
        "admin@bizdnai.com",
    ]
    for email in corporate:
        assert _is_corporate(email), f"Expected corporate: {email}"


def test_missing_at_sign_not_corporate():
    assert not _is_corporate("notanemail")
    assert not _is_corporate("")


# ---------------------------------------------------------------------------
# mx_ok — injectable seam
# ---------------------------------------------------------------------------

def test_mx_ok_returns_true_when_resolver_says_yes():
    assert mx_ok("acme.kz", _resolve=lambda d: True) is True


def test_mx_ok_returns_false_when_resolver_says_no():
    assert mx_ok("acme.kz", _resolve=lambda d: False) is False


def test_mx_ok_empty_domain():
    called = []
    assert mx_ok("", _resolve=lambda d: called.append(d) or True) is False
    assert called == []  # resolver must NOT be called for empty domain


def test_mx_ok_resolver_receives_domain():
    received = []
    mx_ok("corp.kz", _resolve=lambda d: received.append(d) or True)
    assert received == ["corp.kz"]


# ---------------------------------------------------------------------------
# find_corporate_emails
# ---------------------------------------------------------------------------

def test_find_corporate_emails_basic():
    html = "<p>Contact: info@acme.kz or support@gmail.com</p>"
    result = find_corporate_emails(html, _resolve=lambda d: True)
    assert result["has_corporate"] is True
    assert result["has_mx_verified"] is True
    assert "info@acme.kz" in result["corporate"]
    assert "info@acme.kz" in result["mx_valid"]
    assert "support@gmail.com" not in result["corporate"]


def test_find_corporate_emails_no_emails():
    result = find_corporate_emails("no email here", _resolve=lambda d: True)
    assert result["has_corporate"] is False
    assert result["has_mx_verified"] is False
    assert result["corporate"] == []
    assert result["mx_valid"] == []


def test_find_corporate_emails_only_free():
    html = "<p>user@gmail.com and other@yandex.ru</p>"
    result = find_corporate_emails(html, _resolve=lambda d: True)
    assert result["has_corporate"] is False
    assert result["has_mx_verified"] is False


def test_find_corporate_emails_mx_invalid():
    html = "<p>ceo@corp.kz</p>"
    result = find_corporate_emails(html, _resolve=lambda d: False)
    assert result["has_corporate"] is True
    assert result["has_mx_verified"] is False
    assert "ceo@corp.kz" in result["corporate"]
    assert result["mx_valid"] == []


def test_find_corporate_emails_dedupes_mx_calls():
    """Two emails on same domain → resolver called only once."""
    calls = []
    html = "<p>a@corp.kz b@corp.kz</p>"
    find_corporate_emails(html, _resolve=lambda d: calls.append(d) or True)
    assert calls.count("corp.kz") == 1


# ---------------------------------------------------------------------------
# fetch_site — email keys present in returned dict
# ---------------------------------------------------------------------------

def test_fetch_site_returns_email_keys():
    html = "<p>ceo@acme.kz</p>"
    ev = fetch_site("https://acme.kz", _get=lambda u: html, _resolve=lambda d: True)
    assert "has_corporate_email" in ev
    assert "has_mx_verified_email" in ev
    assert "corporate_emails" in ev
    assert "mx_verified_emails" in ev
    assert ev["has_corporate_email"] is True
    assert ev["has_mx_verified_email"] is True


def test_fetch_site_free_email_not_corporate():
    html = "<p>user@gmail.com</p>"
    ev = fetch_site("https://example.kz", _get=lambda u: html, _resolve=lambda d: True)
    assert ev["has_corporate_email"] is False
    assert ev["has_mx_verified_email"] is False


def test_fetch_site_invalid_url_returns_defaults():
    called = []
    ev = fetch_site("", _get=lambda u: called.append(u) or "", _resolve=lambda d: True)
    assert ev["has_ai_disclosure"] is False
    assert called == []


# ---------------------------------------------------------------------------
# G1 _required() — corporate email lifts the floor
# ---------------------------------------------------------------------------

def test_g1_required_true_when_mx_verified():
    site_ev = {
        "has_mx_verified_email": True,
        "has_corporate_email": True,
        "mx_verified_emails": ["info@corp.kz"],
    }
    assert _required("G1", site_ev, {"files": {}, "found": {}}) is True


def test_g1_required_true_when_corporate_only_no_mx():
    site_ev = {
        "has_mx_verified_email": False,
        "has_corporate_email": True,
        "corporate_emails": ["ceo@corp.kz"],
    }
    assert _required("G1", site_ev, {"files": {}, "found": {}}) is True


def test_g1_required_true_when_registry_doc_exists():
    site_ev = {"has_mx_verified_email": False, "has_corporate_email": False}
    docs_ev = {"files": {}, "found": {"registry": True}}
    assert _required("G1", site_ev, docs_ev) is True


def test_g1_required_false_when_no_registry_no_email():
    site_ev = {"has_mx_verified_email": False, "has_corporate_email": False}
    docs_ev = {"files": {}, "found": {}}
    assert _required("G1", site_ev, docs_ev) is False


def test_g1_required_false_when_only_free_email():
    # Free emails on site should NOT lift G1
    site_ev = {
        "has_mx_verified_email": False,
        "has_corporate_email": False,
        "all_emails": ["user@gmail.com"],
    }
    assert _required("G1", site_ev, {"files": {}, "found": {}}) is False


# ---------------------------------------------------------------------------
# _evidence_text — email signal surfaced for all codes
# ---------------------------------------------------------------------------

def test_evidence_text_includes_mx_verified():
    site_ev = {
        "has_mx_verified_email": True,
        "mx_verified_emails": ["info@corp.kz"],
        "has_corporate_email": True,
        "corporate_emails": ["info@corp.kz"],
        "has_ai_disclosure": False,
        "has_consent": False,
        "has_privacy_policy": False,
    }
    text = _evidence_text("G1", site_ev, {"files": {}, "found": {}})
    assert "info@corp.kz" in text
    assert "MX" in text


def test_evidence_text_includes_corporate_no_mx():
    site_ev = {
        "has_mx_verified_email": False,
        "has_corporate_email": True,
        "corporate_emails": ["ceo@corp.kz"],
        "has_ai_disclosure": False,
        "has_consent": False,
        "has_privacy_policy": False,
    }
    text = _evidence_text("G1", site_ev, {"files": {}, "found": {}})
    assert "ceo@corp.kz" in text
    assert "corporate" in text.lower()


def test_evidence_text_no_email_signal_when_absent():
    site_ev = {
        "has_mx_verified_email": False,
        "has_corporate_email": False,
        "has_ai_disclosure": False,
        "has_consent": False,
        "has_privacy_policy": False,
    }
    text = _evidence_text("G1", site_ev, {"files": {}, "found": {}})
    assert "email" not in text.lower()


# ---------------------------------------------------------------------------
# Integration: score_governance with corporate email lifts G1 above floor
# ---------------------------------------------------------------------------

def test_g1_not_floored_when_corporate_email_present(fake_llm):
    """A corporate+MX-verified email on site lifts G1 above the floor."""
    from ati_audit.scorers.governance import score_governance
    from ati_audit.scorers.base import FLOOR
    from ati_audit.config import AuditConfig, Project, Sources, ModelCfg, LLMCfg, SubmitCfg
    cfg = AuditConfig(Project("Acme", False, ""), Sources(), ModelCfg(), LLMCfg(), SubmitCfg())
    site_ev = {
        "has_ai_disclosure": False,
        "has_consent": False,
        "has_privacy_policy": False,
        "has_corporate_email": True,
        "has_mx_verified_email": True,
        "corporate_emails": ["ceo@acme.kz"],
        "mx_verified_emails": ["ceo@acme.kz"],
    }
    docs_ev = {"files": {}, "found": {}}
    high_score = json.dumps({"score": 7, "rationale": "corporate email found", "evidence": []})
    # has_ai=False → G1,G2,G3,G4,G7 scored (5 codes)
    llm = fake_llm([high_score] * 5)
    results = score_governance(cfg, site_ev, docs_ev, llm)
    g1 = next(r for r in results if r.code == "G1")
    assert g1.score is not None
    assert g1.score > FLOOR, f"G1 should exceed floor when corporate email present, got {g1.score}"
