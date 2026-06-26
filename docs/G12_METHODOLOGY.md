# G12 — Infrastructure Hardening: Methodology

**ATI Standard v2 | Direction G12 | Category: Infrastructure**

---

## Overview

G12 measures the **attack surface** of a project's server infrastructure. It answers the question: *how much of the system is unnecessarily exposed to the network, and is that exposure guarded?*

G12 is a **technical universal direction** — it applies to any project that runs server-side infrastructure. Unlike the AI-specific directions (G8–G11), G12 does not require AI usage; it applies whenever the project has internet-facing or network-accessible components.

G12 is **opt-in for the public index.** The direction is always scored locally, but the result is only included in public registry submissions when the project owner explicitly consents. This protects sensitive infrastructure details while preserving the value of the internal audit.

---

## What G12 Measures

G12 evaluates four surface areas:

| Surface | What is checked |
|---------|-----------------|
| **Firewall status** | Is a host-based firewall (e.g., ufw, iptables, nftables) active and enforcing a default-deny inbound policy? |
| **Port exposure** | Which TCP/UDP ports are listening on public interfaces? Are any ports open that should be internal-only (e.g., databases, cache stores, orchestration APIs)? |
| **Container port bypass** | Are containerized services (e.g., Docker) publishing ports in a way that bypasses the host firewall? |
| **Unauthenticated HTTP endpoints** | Do any HTTP/HTTPS endpoints return sensitive data or allow state-changing actions without requiring authentication? |

---

## Scoring Rubric

Base score: **10**

Penalties are applied for each finding. The final score is clamped to **[0, 10]**.

| Finding | Penalty | Cap |
|---------|---------|-----|
| Host firewall is disabled | −2 | — |
| Port is publicly reachable and not protected by firewall | −3 per port | −6 total |
| Sensitive service port (database, cache, orchestration) reachable externally | −1 to −2 per port | — |
| Container port published in a way that bypasses the host firewall | −1 per port | −3 total |
| HTTP/HTTPS endpoint returns data without authentication | −4 | — |

**Score = max(0, 10 − Σ penalties)**

### Rationale for weights

- **Firewall disabled (−2):** Not an immediate breach, but removes a critical defensive layer.
- **Open port bypassing firewall (−3, cap −6):** Direct external exposure of a port that a firewall should block is a high-severity misconfiguration. The cap prevents a single class of finding from zeroing the score alone.
- **Sensitive service port exposed (−1 to −2):** Databases, caches, and internal APIs have no legitimate reason to be internet-accessible. Severity depends on the service type.
- **Container firewall bypass (−1, cap −3):** Docker's default network mode can publish ports on all interfaces, silently defeating ufw/iptables. A known footgun worth penalising.
- **Unauthenticated data endpoint (−4):** An endpoint that returns records, configuration, or PII without credentials is a direct data-exposure risk.

---

## Collection Method

G12 evidence is gathered by a **server-side collector** — a lightweight agent that runs on the host being audited. This design is intentional:

- The collector has access to the local process table, firewall rules, and container metadata.
- Sensitive findings (exact port numbers, service names) stay on the server; only the computed score and redacted rationale are exported.
- The **hostname is hashed** before any export; credentials and secrets in configuration files are redacted.
- Raw scan data never leaves the audited server.

The collector performs:
1. Enumerate listening sockets (`ss -tlnpu` or equivalent).
2. Query firewall status and rules (`ufw status`, `iptables -L`, or equivalent).
3. Enumerate container port mappings (e.g., `docker ps --format`), check if they are bound to all interfaces vs. loopback.
4. Probe a configurable list of HTTP/HTTPS paths for unauthenticated responses.

---

## External Verification (Optional)

An independent external probe can be run from outside the server's network to confirm what is actually reachable from the internet. This serves as a ground-truth check: a port that appears open internally but is blocked at the cloud/datacenter firewall level may score differently under external verification.

**External probing is opt-in** and must only be run against infrastructure that the auditor owns or has explicit written permission to test. Using G12 external probes against third-party systems without authorization may violate applicable law.

When external verification is available, the G12 score reflects the stricter of the two assessments (internal collector vs. external probe), with a note in the rationale.

---

## Privacy by Default

G12 handles inherently sensitive data. The following privacy controls apply:

| Data type | Handling |
|-----------|----------|
| Hostname / IP addresses | Hashed (SHA-256) before export |
| Open port numbers | Grouped by sensitivity class; exact ports stay local |
| Service names and banners | Redacted in exported rationale |
| Credentials found in config | Redacted; presence noted as a finding |
| Raw scan output | Never exported; discarded after scoring |

---

## G12 in the Index

G12 is included in the ATI index mean **only when applicable**:

- `applicable: true` → the project has server infrastructure (set in `ati-audit.yaml`)
- `opt_in_public: true` → the owner consents to include G12 in the public registry submission

When `opt_in_public` is false (default), the direction is scored locally and appears in the local HTML/JSON report, but is excluded from the mean used in any `--submit` payload.

---

## CLI (Roadmap)

Automated G12 collection within the `ati-audit` CLI is planned for a future release. The scoring rubric and methodology described here are stable; the reference collector implementation will conform to this specification.

In the meantime, G12 scores can be entered manually in `ati-audit.yaml` under `overrides.G12` and will be included in the local report.

---

## Changelog

| Version | Change |
|---------|--------|
| v2.1 | G12 introduced as Infrastructure Hardening direction |

---

*ATI Standard by Rashid Kabzhanov — [bizdnai.com/index/](https://bizdnai.com/index/)*
