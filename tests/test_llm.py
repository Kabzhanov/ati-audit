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


def test_openai_client_parses_response(monkeypatch):
    import ati_audit.llm.openai as oai
    canned = {
        "choices": [{"message": {"content": "  Hello from OpenAI  "}}]
    }
    monkeypatch.setattr(oai, "_post", lambda url, headers, payload: canned)
    from ati_audit.config import LLMCfg
    c = oai.OpenAIClient(LLMCfg(provider="openai", model="gpt-4o", api_key_env=""))
    assert c.complete("hi") == "Hello from OpenAI"


def test_anthropic_client_parses_response(monkeypatch):
    import ati_audit.llm.anthropic as ant
    canned = {
        "content": [{"text": "  Hello from Anthropic  "}]
    }
    monkeypatch.setattr(ant, "_post", lambda url, headers, payload: canned)
    from ati_audit.config import LLMCfg
    c = ant.AnthropicClient(LLMCfg(provider="anthropic", model="claude-3-5-sonnet-20241022", api_key_env=""))
    assert c.complete("hi") == "Hello from Anthropic"
