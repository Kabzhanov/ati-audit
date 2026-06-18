# SPDX-License-Identifier: Apache-2.0
import os
import httpx
from ati_audit.config import LLMCfg


def _post(url: str, headers: dict, payload: dict) -> dict:
    return httpx.post(url, headers=headers, json=payload, timeout=60).json()


class OpenAIClient:
    def __init__(self, cfg: LLMCfg):
        self.cfg = cfg
        self.base_url = "https://api.openai.com/v1"

    def complete(self, prompt: str, system: str = "") -> str:
        key = os.environ.get(self.cfg.api_key_env, "")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        resp = _post(
            f"{self.base_url}/chat/completions",
            headers,
            {"model": self.cfg.model, "messages": messages, "max_tokens": 1024},
        )
        return (resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
