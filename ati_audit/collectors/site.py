# SPDX-License-Identifier: Apache-2.0
import re
import httpx

_EMPTY = {"has_ai_disclosure": False, "has_consent": False, "has_privacy_policy": False}


def _default_get(url: str) -> str:
    return httpx.get(url, timeout=30, follow_redirects=True, max_redirects=5).text


_DISCLOSURE = re.compile(r"отвечает\s+ии|answered\s+by\s+ai|ai\s+assistant|🤖", re.I)
_CONSENT = re.compile(r"соглас|consent", re.I)
_PRIVACY = re.compile(r"privacy-policy|privacy|конфиденциальн", re.I)

# ---------------------------------------------------------------------------
# Email verification — official contact on corporate domain
# ---------------------------------------------------------------------------

# Free / shared-mailbox providers that carry NO identity signal.
# Keep alphabetical for easy diffing; add subdomains explicitly (yandex.*).
FREE_EMAIL_DOMAINS = frozenset({
    "gmail.com", "googlemail.com",
    "mail.ru", "inbox.ru", "list.ru", "bk.ru",
    "yandex.ru", "yandex.kz", "yandex.by", "yandex.ua", "yandex.com", "ya.ru",
    "outlook.com", "hotmail.com", "live.com", "msn.com",
    "yahoo.com", "yahoo.co.uk", "yahoo.fr", "yahoo.de", "yahoo.es",
    "icloud.com", "me.com", "mac.com",
    "proton.me", "protonmail.com", "protonmail.ch",
    "gmx.com", "gmx.net", "gmx.de",
    "aol.com",
    "zoho.com",
})

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _extract_emails(html: str) -> list[str]:
    """Return unique email addresses found in *html*, lowercased."""
    return list({m.lower() for m in _EMAIL_RE.findall(html)})


def _email_domain(email: str) -> str:
    return email.split("@", 1)[1] if "@" in email else ""


def _is_corporate(email: str) -> bool:
    """Return True if the email is on a non-free (corporate) domain."""
    dom = _email_domain(email)
    return bool(dom) and dom not in FREE_EMAIL_DOMAINS


def _default_resolve(domain: str) -> bool:
    """Look up MX records for *domain*; return True if at least one exists.

    Uses dnspython when available, otherwise falls back to a subprocess
    nslookup call so the function works in minimal environments too.
    """
    try:
        import dns.resolver  # type: ignore
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        return bool(answers)
    except Exception:
        pass
    # Fallback: nslookup -type=MX
    import subprocess
    try:
        out = subprocess.run(
            ["nslookup", "-type=MX", domain],
            capture_output=True, text=True, timeout=10,
        )
        return "mail exchanger" in out.stdout.lower()
    except Exception:
        return False


def mx_ok(domain: str, _resolve=_default_resolve) -> bool:
    """Return True if *domain* has at least one MX record.

    *_resolve* is an injectable seam: tests pass a fake callable so no
    real DNS queries are made during the test suite.
    """
    if not domain:
        return False
    return _resolve(domain)


def find_corporate_emails(html: str, _resolve=_default_resolve) -> dict:
    """Scan *html* for email addresses and identify corporate ones with valid MX.

    Returns a dict with keys:
        all_emails      list[str] — every email found in the page
        corporate       list[str] — emails on non-free domains
        mx_valid        list[str] — corporate emails whose domain has MX records
        has_corporate   bool      — any corporate email present on page
        has_mx_verified bool      — at least one corporate email with valid MX
    """
    emails = _extract_emails(html)
    corporate = [e for e in emails if _is_corporate(e)]
    # Deduplicate by domain for MX checks (avoid redundant DNS calls)
    checked_domains: dict[str, bool] = {}
    mx_valid: list[str] = []
    for email in corporate:
        dom = _email_domain(email)
        if dom not in checked_domains:
            checked_domains[dom] = mx_ok(dom, _resolve)
        if checked_domains[dom]:
            mx_valid.append(email)
    return {
        "all_emails": emails,
        "corporate": corporate,
        "mx_valid": mx_valid,
        "has_corporate": bool(corporate),
        "has_mx_verified": bool(mx_valid),
    }


def fetch_site(url: str, _get=_default_get, _resolve=_default_resolve) -> dict:
    if not url or not re.match(r"^https?://", url):
        return dict(_EMPTY)
    html = _get(url)
    email_ev = find_corporate_emails(html, _resolve=_resolve)
    return {
        "has_ai_disclosure": bool(_DISCLOSURE.search(html)),
        "has_consent": bool(_CONSENT.search(html)),
        "has_privacy_policy": bool(_PRIVACY.search(html)),
        # Official-contact email trust signal
        "corporate_emails": email_ev["corporate"],
        "mx_verified_emails": email_ev["mx_valid"],
        "has_corporate_email": email_ev["has_corporate"],
        "has_mx_verified_email": email_ev["has_mx_verified"],
    }
