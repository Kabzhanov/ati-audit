# SPDX-License-Identifier: Apache-2.0
import os
import httpx
from ati_audit.config import LLMCfg


def _post(url: str, headers: dict, payload: dict) -> dict:
    return httpx.post(url, headers=headers, json=payload, timeout=60).json()


class AnthropicClient:
    def __init__(self, cfg: LLMCfg):
        self.cfg = cfg

    def complete(self, prompt: str, system: str = "") -> str:
        key = os.environ.get(self.cfg.api_key_env, "")
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "model": self.cfg.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        resp = _post("https://api.anthropic.com/v1/messages", headers, payload)
        content = resp.get("content", [])
        return (content[0].get("text") if content else "").strip()
