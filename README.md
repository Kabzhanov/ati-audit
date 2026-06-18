# ati-audit

Open-source Python CLI that computes the **[AI Trust Index](https://bizdnai.com/index/)** (v2 methodology, G1–G11) for an IT/AI project — entirely on the client side. Nothing but scores leaves your machine.

## What is AI Trust Index?

AI Trust Index (ATI) is a standard for measuring trustworthiness of IT and AI projects across 11 governance directions (G1–G11). It covers systems registry, risk analysis, maturity, compliance, team credentials, customer ratings, governance processes, AI policy, RK Law on AI, ISO 42001, and behavioral robustness (red-team testing).

See full methodology: [bizdnai.com/index/](https://bizdnai.com/index/)

## Install

```bash
pip install ati-audit
# or
pipx install ati-audit
```

## Quick Start

```bash
# 1. Generate config
ati-audit init

# 2. Edit ati-audit.yaml with your project details and LLM API key env var

# 3. Run local audit (nothing leaves your machine)
export OPENAI_API_KEY=sk-...
ati-audit run --self --out report.html

# 4. View report.html in your browser
```

## Methodology v2 — Directions

| Code | Direction | Applicability |
|------|-----------|---------------|
| G1 | Systems registry | Always |
| G2 | Risk analysis | Always |
| G3 | Maturity assessment | Always |
| G4 | Compliance roadmap | Always |
| G5 | IT team verification | Always |
| G6 | Customer ratings | Always (inactive if <3 reviews) |
| G7 | Governance processes | Always |
| G8 | AI usage policy | Only when `has_ai: true` |
| G9 | RK Law on AI | Only when `has_ai: true` |
| G10 | ISO/IEC 42001 | Only when `has_ai: true` |
| G11 | Behavioral robustness | Only when `has_ai: true` |

**Index = mean of active & applicable directions.**

## CLI Reference

```bash
ati-audit init                          # Generate ati-audit.yaml
ati-audit run                           # Run full audit (reads ati-audit.yaml)
ati-audit run --only G11                # Run only one direction
ati-audit run --out report.html         # Save HTML report
ati-audit run --submit --registry URL   # Send scores to registry (no raw data)
ati-audit probes list                   # List G11 red-team probes
```

## Configuration (`ati-audit.yaml`)

```yaml
project:
  name: "My Project"
  has_ai: true          # auto-detected from model.base_url if omitted
  site_url: "https://example.com"

sources:
  docs_path: "./docs"               # .md/.txt docs scanned for evidence
  credentials_path: "./creds"       # team credential documents for G5

model:  # the AUDITED model (for G11 red-team)
  connector: openai                 # openai | anthropic | http
  base_url: "http://localhost:11434/v1"
  model: llama3
  api_key_env: MODEL_API_KEY

llm:   # the JUDGE/ANALYZER (bring-your-own-key)
  provider: openai
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY

submit:
  registry_url: "https://bizdnai.com/api/ati/submit"
```

## Privacy

Raw documents, source code, model responses, and PII **never leave your machine**. See [SECURITY.md](SECURITY.md) for the full privacy invariant.

## License

Apache-2.0. See [LICENSE](LICENSE).
