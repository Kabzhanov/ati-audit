# SPDX-License-Identifier: Apache-2.0
"""Local PII redaction. Source of truth mirrors planet/ati_public/pii.py."""
import re

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE = re.compile(r"(?<!\w)(\+?\d[\d\s().-]{7,}\d)(?!\w)")


def redact(text: str) -> str:
    if not text:
        return text or ""
    text = _EMAIL.sub("[redacted]", text)
    text = _PHONE.sub("[redacted]", text)
    return text
