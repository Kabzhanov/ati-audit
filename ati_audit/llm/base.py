# SPDX-License-Identifier: Apache-2.0
from typing import Protocol
from ati_audit.config import LLMCfg


class LLMClient(Protocol):
    def complete(self, prompt: str, system: str = "") -> str: ...


def make_client(cfg: LLMCfg) -> LLMClient:
    if cfg.provider == "openai":
        from ati_audit.llm.openai import OpenAIClient
        return OpenAIClient(cfg)
    if cfg.provider == "anthropic":
        from ati_audit.llm.anthropic import AnthropicClient
        return AnthropicClient(cfg)
    if cfg.provider == "http":
        from ati_audit.llm.http import HttpClient
        return HttpClient(cfg)
    raise ValueError(f"unknown llm provider: {cfg.provider}")
