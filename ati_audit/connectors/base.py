# SPDX-License-Identifier: Apache-2.0
import os
import httpx
from typing import Protocol
from ati_audit.config import ModelCfg


class ModelConnector(Protocol):
    def ask(self, prompt: str) -> str: ...


def _post(url: str, headers: dict, payload: dict) -> dict:
    return httpx.post(url, headers=headers, json=payload, timeout=60).json()


class OpenAIConnector:
    """Connects to an OpenAI-compatible endpoint (the AUDITED model)."""
    def __init__(self, cfg: ModelCfg):
        self.cfg = cfg

    def ask(self, prompt: str) -> str:
        key = os.environ.get(self.cfg.api_key_env, "")
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        resp = _post(
            f"{self.cfg.base_url}/chat/completions",
            headers,
            {"model": self.cfg.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512},
        )
        return (resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()


class AnthropicConnector:
    """Connects to Anthropic Messages API (the AUDITED model)."""
    def __init__(self, cfg: ModelCfg):
        self.cfg = cfg

    def ask(self, prompt: str) -> str:
        key = os.environ.get(self.cfg.api_key_env, "")
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        resp = _post(
            "https://api.anthropic.com/v1/messages",
            headers,
            {"model": self.cfg.model, "max_tokens": 512,
             "messages": [{"role": "user", "content": prompt}]},
        )
        content = resp.get("content", [])
        return (content[0].get("text") if content else "").strip()


class HttpConnector:
    """Generic HTTP connector (the AUDITED model)."""
    def __init__(self, cfg: ModelCfg):
        self.cfg = cfg

    def ask(self, prompt: str) -> str:
        resp = _post(self.cfg.base_url, {}, {"prompt": prompt, "max_tokens": 512})
        return (resp.get("text") or "").strip()


def make_connector(cfg: ModelCfg) -> ModelConnector:
    if cfg.connector == "openai":
        return OpenAIConnector(cfg)
    if cfg.connector == "anthropic":
        return AnthropicConnector(cfg)
    if cfg.connector == "http":
        return HttpConnector(cfg)
    raise ValueError(f"unknown connector kind: {cfg.connector}")
