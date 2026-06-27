<p align="center">
  <h1 align="center">🛡️ ati-audit</h1>
  <p align="center">
    The open auditor for the <strong>AI Trust Index</strong> — one honest 0–10 number for how responsibly an IT/AI project is built.
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0"></a>
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python 3.11+">
    <a href="https://github.com/Kabzhanov/ati-audit/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
    <a href="https://bizdnai.com/index/"><img src="https://img.shields.io/badge/Standard-ATI_Open_Standard-blueviolet" alt="ATI Open Standard"></a>
  </p>
</p>

---

> **Sibling project:** [ValIQ](https://github.com/Kabzhanov/valiq) — the valuation companion that converts your ATI score into a USD product valuation range.

---

## 📊 What is the AI Trust Index?

The **AI Trust Index (ATI)** is an open standard that distills responsible IT and AI governance into a single, comparable **0–10 score** across 12 structured directions (G1–G12). It is universal: every IT project can be audited on the governance directions (G1–G7) and the infrastructure hardening direction (G12); AI-specific directions (G8–G11) only apply — and only count — when the project actually uses AI.

The standard is created by **Rashid Kabzhanov**. Full methodology and public registry: [bizdnai.com/index/](https://bizdnai.com/index/)

---

## ✨ Key Features

- **Universal IT + AI scope** — meaningful score for any software project; AI directions activate only when relevant
- **12 structured directions G1–G12** — from systems registry and risk analysis through behavioral red-teaming and infrastructure hardening
- **Infrastructure attack-surface audit (G12)** — checks firewall status, exposed ports, container network bypass, and unauthenticated endpoints; privacy-first: sensitive data never leaves the host
- **Jurisdiction-aware national-law compliance (G9)** — selects the applicable law by `project.country`; extensible registry, contributions welcome
- **Behavioral red-team of the live model (G11)** — actually probes the running model endpoint, not just reads the system prompt
- **Privacy-first** — runs entirely on your machine; `--submit` sends only computed scores + optional signature, never raw documents or PII
- **Bring-your-own-key LLM** — any OpenAI-compatible endpoint (cloud or local Ollama/vLLM) as the judge
- **Honest defaults** — no evidence found → low score; nothing is assumed or fabricated

---

## 📐 Methodology (v2)

### Universal directions — always scored

| Code | Direction | Notes |
|------|-----------|-------|
| G1 | Systems registry | Documents the project's systems and components; a verified official contact email on a corporate domain (non-free provider, valid MX) is also counted as a positive identity signal |
| G2 | Risk analysis | Identified and documented risks |
| G3 | Maturity assessment | Process and product maturity evidence |
| G4 | Compliance roadmap | Planned path to regulatory conformity |
| G5 | IT team verification | Team credentials and competency evidence |
| G6 | Customer ratings | Verified user feedback (inactive if < 3 reviews) |
| G7 | Governance processes | Policies, controls, oversight (hinge — always applies) |

### AI-specific directions — scored only when `has_ai: true`

| Code | Direction | Notes |
|------|-----------|-------|
| G8 | AI usage policy | Documented policy for AI system use |
| G9 | National AI-law compliance | Jurisdiction-aware; driven by `project.country` |
| G10 | ISO/IEC 42001 | AI management system alignment |
| G11 | Behavioral robustness | Live red-team probing of the model endpoint |

### Infrastructure direction — scored when the project has server infrastructure

| Code | Direction | Notes |
|------|-----------|-------|
| G12 | Infrastructure hardening | Attack-surface audit: firewall status, exposed ports, container network bypass, unauthenticated endpoints. **Opt-in for public index** — scored locally by default; included in `--submit` payload only with explicit owner consent. See [`docs/G12_METHODOLOGY.md`](docs/G12_METHODOLOGY.md) for the full rubric. |

**Index = mean of all active and applicable directions.**

---

## 🚀 Install

Not yet on PyPI — install from source:

```bash
pip install git+https://github.com/Kabzhanov/ati-audit
```

Once published to PyPI you will be able to use:

```bash
pip install ati-audit
# or
pipx install ati-audit
```

Requires **Python 3.11+**.

---

## ⚡ Quickstart

```bash
# 1. Generate a config file
ati-audit init

# 2. Edit ati-audit.yaml with your project details and set your LLM API key
export OPENAI_API_KEY=sk-...

# 3. Run a local audit — nothing leaves your machine
ati-audit run --self --out report.html

# 4. Open report.html in your browser
```

### Audit a single direction

```bash
ati-audit run --only G11          # Run behavioral red-team only
ati-audit probes list             # List all G11 red-team probes
```

### Annotated `ati-audit.yaml`

```yaml
project:
  name: "My IT Project"          # Display name
  has_ai: true                   # true → G8–G11 scored; false → G1–G7 only
  site_url: "https://example.com" # Scanned for AI disclosure, consent, privacy policy
  country: KZ                    # ISO 3166-1 alpha-2 — drives G9 jurisdiction check

sources:
  docs_path: "./docs"            # .md/.txt/.rst docs scanned for evidence
  credentials_path: "./creds"    # Team credential documents (PDFs, text) for G5

model:                           # The AUDITED model (used for G11 red-team)
  connector: "openai"            # openai | anthropic | http
  base_url: "http://localhost:11434/v1"  # OpenAI-compatible endpoint (Ollama, vLLM, etc.)
  model: "llama3"
  api_key_env: "MODEL_API_KEY"   # API key read from env — never written to disk

llm:                             # The JUDGE/ANALYZER (bring-your-own-key)
  provider: "openai"             # openai | anthropic | http
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
```

---

## 🌍 Jurisdictions (G9)

The `project.country` field (ISO 3166-1 alpha-2) selects the applicable national AI and data-protection law for the G9 compliance check.

**Seeded countries:**

| Code | Jurisdiction | Law / Framework |
|------|-------------|-----------------|
| KZ | Kazakhstan | Law No. 230-VIII on Artificial Intelligence (in force 2026-01-16) |
| EU | European Union | EU AI Act (Regulation (EU) 2024/1689) |
| US | United States | NIST AI Risk Management Framework + sectoral rules |
| GB | United Kingdom | UK pro-innovation AI principles + UK GDPR / DPA 2018 |
| RU | Russia | Federal data law 152-FZ + AI Code of Ethics |

**Unknown country** → the LLM assesses against general national law knowledge and flags the rationale as a general assessment.

**Contributions welcome:** add your country to [`ati_audit/jurisdictions.yaml`](ati_audit/jurisdictions.yaml) and open a PR.

---

## 🔒 Privacy & Security

`ati-audit` is built on a strict privacy invariant: **raw documents, source code, model responses, and PII never leave your machine.**

When `--submit` is used, the payload contains only:
- The computed index score
- Per-direction results (scores, active/applicable flags, redacted rationale snippets)
- Project name and public site URL
- An optional cryptographic signature

LLM API keys are read from environment variables and are never written to disk or included in any payload.

The G11 probe suite is published for **transparency and authorized safety testing only** — intended for organizations auditing their own systems. Using probes against systems you do not own or have explicit permission to test may violate applicable laws.

See [`SECURITY.md`](SECURITY.md) for the full privacy invariant, PII redaction scope, and vulnerability reporting instructions.

---

## 🆓 Free vs. Verified

| | Self-audit (`--submit` not used) | Verified badge |
|---|---|---|
| Runs locally | Yes | Yes |
| Cost | Free | Hosted service |
| Result | Local HTML/JSON report | Entry in public ATI registry |
| Monitoring | No | Yes |

The self-audit (`ati-audit run --self`) is **free, open-source, and runs entirely on your machine**. Verified badges, public registry listings, and continuous monitoring are a hosted service at [bizdnai.com/index/](https://bizdnai.com/index/) and are not part of this repository.

---

## 🤝 Contributing

PRs are welcome, especially for:
- **New jurisdictions** — add an entry to [`ati_audit/jurisdictions.yaml`](ati_audit/jurisdictions.yaml)
- **New G11 probes** — extend [`ati_audit/probes/core.yaml`](ati_audit/probes/core.yaml)
- **G12 collector** — a server-side agent implementing the [`docs/G12_METHODOLOGY.md`](docs/G12_METHODOLOGY.md) rubric; CLI integration is on the roadmap

Before submitting, run:

```bash
pytest -q
ruff check ati_audit
```

---

## 📄 License & Author

Licensed under the **Apache-2.0** License. See [`LICENSE`](LICENSE).

AI Trust Index standard by **Rashid Kabzhanov** — [bizdnai.com/index/](https://bizdnai.com/index/)
