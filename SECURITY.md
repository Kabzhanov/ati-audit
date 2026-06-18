# Security Policy

## Privacy Invariant

`ati-audit` is designed so that **no raw data ever leaves your machine**.

The `--submit` payload contains ONLY:
- The computed index score (a float)
- Per-direction results: `{code, score, active, applicable, rationale_redacted, evidence_categories}`
- Project metadata: name and public site URL
- An optional cryptographic signature

**What is NEVER transmitted:**
- Source code or repository contents
- Documentation files or their text content
- Team credential documents (diplomas, certificates, etc.)
- Raw model responses from G11 red-team probes
- Any PII (emails, phone numbers, names) — rationale is passed through `pii.redact()` before inclusion
- The HTML content of your site
- Any API keys or secrets

LLM API keys are read from environment variables and never written to disk or included in any payload.

## Dual-Use Statement

The probe suite (`ati_audit/probes/core.yaml`) is published for **transparency and authorized
safety testing only**. It is intended for organizations auditing their own AI systems. Using these
probes against systems you do not own or have explicit permission to test may violate applicable laws.

The probes are tagged with direction codes and law references (RK Law on AI, ISO 42001) to support
regulatory compliance frameworks. They are designed to be defensive, not offensive.

## Reporting Vulnerabilities

If you discover a security vulnerability in `ati-audit`, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities.
2. Email the maintainers at: kabzhanov@gmail.com
3. Include a description of the vulnerability, reproduction steps, and potential impact.
4. We will respond within 5 business days and work to address critical issues promptly.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
