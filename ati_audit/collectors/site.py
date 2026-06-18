# SPDX-License-Identifier: Apache-2.0
import re
import httpx


def _default_get(url: str) -> str:
    return httpx.get(url, timeout=30, follow_redirects=True).text


_DISCLOSURE = re.compile(r"отвечает\s+ии|answered\s+by\s+ai|ai\s+assistant|🤖", re.I)
_CONSENT = re.compile(r"соглас|consent", re.I)
_PRIVACY = re.compile(r"privacy-policy|privacy|конфиденциальн", re.I)


def fetch_site(url: str, _get=_default_get) -> dict:
    html = _get(url) if url else ""
    return {
        "html": html,
        "has_ai_disclosure": bool(_DISCLOSURE.search(html)),
        "has_consent": bool(_CONSENT.search(html)),
        "has_privacy_policy": bool(_PRIVACY.search(html)),
    }
