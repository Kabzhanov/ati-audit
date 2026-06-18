# SPDX-License-Identifier: Apache-2.0
import re
import httpx

_EMPTY = {"has_ai_disclosure": False, "has_consent": False, "has_privacy_policy": False}


def _default_get(url: str) -> str:
    return httpx.get(url, timeout=30, follow_redirects=True, max_redirects=5).text


_DISCLOSURE = re.compile(r"отвечает\s+ии|answered\s+by\s+ai|ai\s+assistant|🤖", re.I)
_CONSENT = re.compile(r"соглас|consent", re.I)
_PRIVACY = re.compile(r"privacy-policy|privacy|конфиденциальн", re.I)


def fetch_site(url: str, _get=_default_get) -> dict:
    if not url or not re.match(r"^https?://", url):
        return dict(_EMPTY)
    html = _get(url)
    return {
        "has_ai_disclosure": bool(_DISCLOSURE.search(html)),
        "has_consent": bool(_CONSENT.search(html)),
        "has_privacy_policy": bool(_PRIVACY.search(html)),
    }
