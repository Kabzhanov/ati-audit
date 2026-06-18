# SPDX-License-Identifier: Apache-2.0
import pytest
from ati_audit.llm.base import make_client
from ati_audit.connectors.base import make_connector


def test_http_client_uses_transport(monkeypatch):
    import ati_audit.llm.http as h
    monkeypatch.setattr(h, "_post", lambda url, payload: {"text": "ok"})
    from ati_audit.config import LLMCfg
    c = make_client(LLMCfg(provider="http", model="x", api_key_env=""))
    assert c.complete("hi") == "ok"


def test_unknown_provider_raises():
    from ati_audit.config import LLMCfg
    with pytest.raises(ValueError):
        make_client(LLMCfg(provider="nope"))
