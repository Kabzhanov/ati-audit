# SPDX-License-Identifier: Apache-2.0
import textwrap
from ati_audit.config import load_config


def _write(tmp_path, body):
    p = tmp_path / "c.yaml"
    p.write_text(textwrap.dedent(body))
    return str(p)


def test_loads_and_resolves_has_ai_explicit(tmp_path):
    cfg = load_config(_write(tmp_path, """
        project: {name: Acme, has_ai: false, site_url: "https://acme.test"}
        llm: {provider: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY}
    """))
    assert cfg.project.name == "Acme"
    assert cfg.project.has_ai is False


def test_autodetect_has_ai_from_model_endpoint(tmp_path):
    cfg = load_config(_write(tmp_path, """
        project: {name: Acme, site_url: "https://acme.test"}
        model: {connector: openai, base_url: "http://localhost:11434/v1", model: llama3}
        llm: {provider: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY}
    """))
    assert cfg.project.has_ai is True
