# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
import yaml


@dataclass
class Project:
    name: str = ""
    has_ai: bool = False
    site_url: str = ""


@dataclass
class Sources:
    repo_path: str = ""
    docs_path: str = ""
    credentials_path: str = ""


@dataclass
class ModelCfg:
    connector: str = ""
    base_url: str = ""
    model: str = ""
    api_key_env: str = ""


@dataclass
class LLMCfg:
    provider: str = ""
    model: str = ""
    api_key_env: str = ""


@dataclass
class SubmitCfg:
    registry_url: str = ""


@dataclass
class AuditConfig:
    project: Project
    sources: Sources
    model: ModelCfg
    llm: LLMCfg
    submit: SubmitCfg


def load_config(path: str) -> AuditConfig:
    raw = yaml.safe_load(open(path, encoding="utf-8")) or {}
    proj_raw = raw.get("project", {})
    model = ModelCfg(**raw.get("model", {}))
    project = Project(
        **{k: proj_raw[k] for k in ("name", "site_url") if k in proj_raw},
        has_ai=proj_raw.get("has_ai", bool(model.base_url)),
    )
    return AuditConfig(
        project,
        Sources(**raw.get("sources", {})),
        model,
        LLMCfg(**raw.get("llm", {})),
        SubmitCfg(**raw.get("submit", {})),
    )
