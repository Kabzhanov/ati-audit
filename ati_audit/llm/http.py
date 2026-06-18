# SPDX-License-Identifier: Apache-2.0
import os
import httpx
from ati_audit.config import LLMCfg


def _post(url: str, payload: dict) -> dict:
    return httpx.post(url, json=payload, timeout=60).json()


class HttpClient:
    def __init__(self, cfg: LLMCfg):
        self.url = os.environ.get("ATI_LLM_URL", "http://127.0.0.1:3088/ai/complete")

    def complete(self, prompt: str, system: str = "") -> str:
        p = (system + "\n\n" + prompt) if system else prompt
        return (_post(self.url, {"prompt": p, "max_tokens": 1024}).get("text") or "").strip()
