# SPDX-License-Identifier: Apache-2.0
import httpx
from ati_audit.pii import redact


def build_payload(report: dict) -> dict:
    dirs = [
        {
            "code": d["code"],
            "score": d["score"],
            "active": d["active"],
            "applicable": d["applicable"],
            "rationale_redacted": redact(d.get("rationale", "")),
            "evidence_categories": d.get("evidence_categories", []),
        }
        for d in report.get("directions", [])
    ]
    return {
        "index": report["index"],
        "directions": dirs,
        "project_meta": {
            "name": report.get("project", {}).get("name", ""),
            "site_url": report.get("project", {}).get("site_url", ""),
        },
        "signature": None,
    }


def sign(payload: dict, key_pem: bytes) -> str:
    import json
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = load_pem_private_key(key_pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("signing key must be ed25519")
    signing_input = {k: v for k, v in payload.items() if k != "signature"}
    return key.sign(json.dumps(signing_input, sort_keys=True).encode()).hex()


def _default_post(url, json_data):
    try:
        return httpx.post(url, json=json_data, timeout=60).json()
    except (httpx.HTTPError, ValueError) as e:
        return {"error": str(e)}


def submit(payload: dict, registry_url: str, _post=_default_post) -> dict:
    return _post(registry_url, payload)
