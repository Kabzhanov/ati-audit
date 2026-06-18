# SPDX-License-Identifier: Apache-2.0
import pytest
from ati_audit.submit import build_payload, sign, submit


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


def _make_ed25519_pem() -> bytes:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, NoEncryption,
    )
    key = Ed25519PrivateKey.generate()
    return key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())


def test_sign_ed25519_produces_hex():
    pem = _make_ed25519_pem()
    payload = {"index": 7.0, "signature": None}
    sig = sign(payload, pem)
    assert isinstance(sig, str)
    assert len(sig) == 128  # 64 bytes → 128 hex chars
    # Verify it's valid hex
    bytes.fromhex(sig)


def test_sign_excludes_signature_key_from_input():
    """Signing with signature=None and signature=anything must give the same result."""
    pem = _make_ed25519_pem()
    payload_a = {"index": 7.0, "signature": None}
    payload_b = {"index": 7.0, "signature": "old_sig"}
    assert sign(payload_a, pem) == sign(payload_b, pem)


def test_sign_non_ed25519_raises():
    from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, NoEncryption,
    )
    import os
    rsa_key = generate_private_key(65537, 2048)
    pem = rsa_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    with pytest.raises(ValueError, match="ed25519"):
        sign({"index": 1.0}, pem)
