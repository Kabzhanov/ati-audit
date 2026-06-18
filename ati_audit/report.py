# SPDX-License-Identifier: Apache-2.0
import html as _html
from datetime import datetime, timezone
from ati_audit.aggregate import compute_index

NAMES = {
    "G1": "Systems registry",
    "G2": "Risk analysis",
    "G3": "Maturity assessment",
    "G4": "Compliance roadmap",
    "G5": "IT team verification",
    "G6": "Customer ratings",
    "G7": "Governance processes",
    "G8": "AI usage policy",
    "G9": "National AI-law compliance",
    "G10": "ISO/IEC 42001",
    "G11": "Behavioral robustness",
}


def build_report(cfg, results) -> dict:
    directions = [
        {
            "code": r.code,
            "name": NAMES.get(r.code, r.code),
            "score": r.score,
            "active": r.active,
            "applicable": r.applicable,
            "rationale": r.rationale,
            "evidence_categories": sorted({e.category for e in r.evidence}),
        }
        for r in results
    ]
    return {
        "index": compute_index(results),
        "project": {"name": cfg.project.name, "site_url": cfg.project.site_url},
        "directions": directions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def to_html(report: dict) -> str:
    index = report.get("index", 0)
    project = report.get("project", {})
    directions = report.get("directions", [])
    rows = ""
    for d in directions:
        score_str = str(d["score"]) if d["score"] is not None else "N/A"
        active_str = "active" if d["active"] else "inactive"
        applicable_str = "" if d["applicable"] else " (N/A)"
        rows += (
            f"<tr>"
            f"<td>{d['code']}</td>"
            f"<td>{d['name']}</td>"
            f"<td>{score_str}</td>"
            f"<td>{active_str}{applicable_str}</td>"
            f"<td>{_html.escape(d.get('rationale', '')[:200])}</td>"
            f"</tr>\n"
        )
    safe_name = _html.escape(project.get("name", ""))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ATI Audit Report — {safe_name}</title>
<style>
  body {{ font-family: sans-serif; background: #1a1a2e; color: #e0e0e0; margin: 2rem; }}
  h1 {{ color: #a78bfa; }}
  .index {{ font-size: 3rem; color: #34d399; font-weight: bold; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th {{ background: #2d2d5e; color: #a78bfa; padding: 0.5rem; text-align: left; }}
  td {{ padding: 0.5rem; border-bottom: 1px solid #333; }}
  tr:hover {{ background: #22223b; }}
</style>
</head>
<body>
<h1>AI Trust Index Audit — {safe_name}</h1>
<p>Site: {_html.escape(project.get('site_url', ''))}</p>
<p>Generated: {report.get('generated_at', '')}</p>
<div class="index">{index} / 10</div>
<table>
<thead><tr><th>Code</th><th>Direction</th><th>Score</th><th>Status</th><th>Rationale</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>"""
