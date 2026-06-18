# SPDX-License-Identifier: Apache-2.0
from ati_audit.models import ScoreResult
from ati_audit.scorers.base import grounded_score
from ati_audit.jurisdictions import load_jurisdictions

RUBRICS = {
    "G1": (
        "G1 Systems Registry: Does the project maintain a documented registry of all IT systems, "
        "data flows, and integrations? Score 1-10: 1=no registry, 5=informal/partial, "
        "10=complete formal registry with versions and owners."
    ),
    "G2": (
        "G2 Risk Analysis: Is there documented risk analysis covering technical, legal, operational, "
        "and AI-specific risks? Score 1-10: 1=no risk docs, 5=partial/informal, "
        "10=complete structured risk register with mitigations."
    ),
    "G3": (
        "G3 Maturity Assessment: Has the project formally assessed its IT/AI maturity level "
        "(e.g., CMMI, digital maturity)? Score 1-10: 1=no assessment, 5=informal self-assessment, "
        "10=formal external assessment with documented results."
    ),
    "G4": (
        "G4 Compliance Roadmap: Is there a documented roadmap for achieving regulatory and standards "
        "compliance? Score 1-10: 1=no roadmap, 5=informal plans, "
        "10=detailed roadmap with milestones, owners, and timelines."
    ),
    "G7": (
        "G7 Governance Processes: Are there documented governance processes for decision-making, "
        "change management, and oversight (including AI governance if applicable)? "
        "Score 1-10: 1=no processes documented, 5=some informal processes, "
        "10=comprehensive formal governance framework."
    ),
    "G8": (
        "G8 AI Usage Policy: Is there a clear, published AI usage policy covering acceptable use, "
        "transparency, data handling, and user consent? "
        "Score 1-10: 1=no policy, 5=draft/partial policy, "
        "10=comprehensive published policy with versioning and enforcement."
    ),
    "G10": (
        "G10 ISO/IEC 42001 (AIMS): Does the project implement or work toward ISO/IEC 42001 "
        "AI Management System standard? "
        "Score 1-10: 1=not considered, 5=awareness/planning stage, "
        "10=implemented AIMS with documented policies, risks, and objectives."
    ),
}


def _g9_rubric(country: str, jurisdictions: dict) -> tuple[str, str]:
    """Return (rubric_text, jurisdiction_label) for G9, based on the client's country.

    If the country is found in the registry, reference its law and requirements.
    If not found (or empty), instruct the LLM to use general knowledge and flag it.
    """
    code = (country or "").upper().strip()
    if code and code in jurisdictions:
        j = jurisdictions[code]
        reqs = "\n".join(f"  - {r}" for r in j.get("requirements", []))
        rubric = (
            f"G9 National AI-law compliance: Does the project comply with {j['law']} ({j['ref']})? "
            f"Required compliance areas:\n{reqs}\n"
            "Score 1-10: 1=no evidence of compliance, 5=partial/informal, "
            "10=documented compliance program with evidence for all requirements."
        )
        label = f"{j['name']}: {j['ref']}"
    else:
        jurisdiction_desc = f"the national AI and data-protection laws of {country}" if country \
            else "the applicable national AI and data-protection laws of the client jurisdiction"
        rubric = (
            f"G9 National AI-law compliance: Does the project comply with {jurisdiction_desc}? "
            "Use your general knowledge of national AI/data-protection regulations. "
            "Score 1-10: 1=no evidence of compliance, 5=partial/informal, "
            "10=documented compliance program with evidence of consent and disclosures. "
            "NOTE: This is a general assessment — the jurisdiction was not found in the registry."
        )
        label = "general assessment (jurisdiction not in registry)"
    return rubric, label


def _required(code: str, site_ev: dict, docs_ev: dict) -> bool:
    """Return True ONLY if the required artifact is actually present in collected evidence.

    Honest-defaults principle (spec §4): absence of evidence is NOT benefit of the doubt — a
    missing artifact floors the score. This is the deterministic guard against an ungrounded
    high LLM score, regardless of whether docs were simply not provided or scanned-and-absent.
    """
    files = docs_ev.get("files", {})
    found = docs_ev.get("found", {})
    if code == "G1":
        return found.get("registry", False)
    if code == "G2":
        return found.get("risk", False)
    if code == "G3":
        return found.get("policy", False) or found.get("process", False)
    if code == "G4":
        return found.get("roadmap", False)
    if code == "G7":
        return found.get("process", False)
    if code == "G8":
        return found.get("policy", False)
    if code == "G9":
        return site_ev.get("has_consent", False) or site_ev.get("has_ai_disclosure", False)
    if code == "G10":
        blob = " ".join(files.values()).lower()
        return "iso" in blob or "aims" in blob or "42001" in blob
    return False


def _evidence_text(code: str, site_ev: dict, docs_ev: dict) -> str:
    parts = []
    # Add relevant doc snippets (truncated)
    for name, text in docs_ev.get("files", {}).items():
        snippet = text[:500]
        parts.append(f"[{name}]\n{snippet}")
    # Add site evidence
    if site_ev.get("has_ai_disclosure"):
        parts.append("[site] AI disclosure banner detected")
    if site_ev.get("has_consent"):
        parts.append("[site] consent language detected")
    if site_ev.get("has_privacy_policy"):
        parts.append("[site] privacy policy link detected")
    text = "\n\n".join(parts) or "(no evidence collected)"
    return text[:8000]


_AI_CODES = {"G8", "G9", "G10"}
_GOV_CODES = ["G1", "G2", "G3", "G4", "G7", "G8", "G9", "G10"]


def score_governance(cfg, site_ev: dict, docs_ev: dict, llm) -> list[ScoreResult]:
    jurisdictions = load_jurisdictions()
    country = getattr(cfg.project, "country", "") or ""
    results = []
    for code in _GOV_CODES:
        applicable = cfg.project.has_ai if code in _AI_CODES else True
        if not applicable:
            results.append(
                ScoreResult(
                    code, None, active=False, applicable=False,
                    rationale="not applicable (no AI in project)", evidence=[]
                )
            )
            continue
        required = _required(code, site_ev, docs_ev)
        evidence_text = _evidence_text(code, site_ev, docs_ev)
        if code == "G9":
            rubric, jurisdiction_label = _g9_rubric(country, jurisdictions)
            result = grounded_score(
                code, llm, evidence_text, rubric,
                required_present=required, applicable=True,
            )
            # Prepend jurisdiction label to rationale so report shows which law was used
            result = ScoreResult(
                result.code, result.score, result.active, result.applicable,
                f"[{jurisdiction_label}] {result.rationale}",
                result.evidence,
            )
        else:
            result = grounded_score(
                code, llm, evidence_text, RUBRICS[code],
                required_present=required, applicable=True,
            )
        results.append(result)
    return results
