# SPDX-License-Identifier: Apache-2.0
from ati_audit.pii import redact


def test_redacts_emails_and_phones():
    s = "Contact ivan@example.com or +7 707 333 3481 please"
    out = redact(s)
    assert "ivan@example.com" not in out
    assert "+7 707 333 3481" not in out
    assert "[redacted]" in out.lower() or "***" in out


def test_keeps_plain_text():
    assert redact("AI usage policy v1.0 exists") == "AI usage policy v1.0 exists"
