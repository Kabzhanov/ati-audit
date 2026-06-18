# SPDX-License-Identifier: Apache-2.0
"""CLI entry point: ati-audit init / run / probes."""
import argparse
import json
import os
import shutil
import sys

from ati_audit.config import load_config, AuditConfig
from ati_audit.collectors.site import fetch_site
from ati_audit.collectors.docs import scan_docs
from ati_audit.scorers.governance import score_governance
from ati_audit.scorers.team import score_team
from ati_audit.scorers.reviews import score_reviews
from ati_audit.scorers.redteam import score_redteam
from ati_audit.report import build_report, to_html
from ati_audit.submit import build_payload, sign, submit
from ati_audit.probing import load_probes
from ati_audit.aggregate import compute_index

_EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
_EXAMPLE_CONFIG = os.path.join(_EXAMPLES_DIR, "ati-audit.yaml")


def run_audit(cfg: AuditConfig, *, llm=None, connector=None, reviews=None) -> dict:
    """Orchestrate all collectors and scorers. llm/connector injectable for tests."""
    if llm is None:
        from ati_audit.llm.base import make_client
        llm = make_client(cfg.llm)
    if connector is None and cfg.project.has_ai and cfg.model.connector:
        from ati_audit.connectors.base import make_connector
        connector = make_connector(cfg.model)

    site_ev = fetch_site(cfg.project.site_url) if cfg.project.site_url else {
        "has_ai_disclosure": False, "has_consent": False, "has_privacy_policy": False,
    }
    docs_ev = scan_docs(cfg.sources.docs_path) if cfg.sources.docs_path else {
        "files": {}, "found": {k: False for k in ("policy", "registry", "risk", "process", "roadmap")},
    }

    results = []
    results.extend(score_governance(cfg, site_ev, docs_ev, llm))
    results.append(score_team(cfg, llm))
    results.append(score_reviews(reviews if reviews is not None else []))

    # G11 — only if has_ai and connector available
    if cfg.project.has_ai and connector is not None:
        results.append(score_redteam(cfg, connector, llm))
    else:
        from ati_audit.models import ScoreResult
        if cfg.project.has_ai and not cfg.model.base_url:
            print(
                "Warning: G11 behavioral testing skipped — no model endpoint configured (model.base_url).",
                file=sys.stderr,
            )
        results.append(
            ScoreResult("G11", None, False, cfg.project.has_ai,
                        "not applicable (no AI in project)" if not cfg.project.has_ai
                        else "no model connector configured", [])
        )

    return build_report(cfg, results)


def _cmd_init(args):
    dest = args.output or "ati-audit.yaml"
    src = os.path.abspath(_EXAMPLE_CONFIG)
    if not os.path.exists(src):
        print(f"Example config not found at {src}", file=sys.stderr)
        return 1
    shutil.copy(src, dest)
    print(f"Created {dest} — edit it then run: ati-audit run")
    return 0


def _cmd_run(args):
    cfg = load_config(args.config)

    only = args.only  # e.g. "G11"
    rep = run_audit(cfg, reviews=[])

    if only:
        rep["directions"] = [d for d in rep["directions"] if d["code"] == only]
        from ati_audit.models import ScoreResult
        # Recompute index over filtered directions only
        filtered_results = [
            ScoreResult(d["code"], d["score"], d["active"], d["applicable"], "", [])
            for d in rep["directions"]
        ]
        rep["index"] = compute_index(filtered_results)
        rep["partial"] = True

    out_path = args.out
    if out_path and out_path.endswith(".html"):
        content = to_html(rep)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"HTML report written to {out_path}")
    elif out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(rep, indent=2))
        print(f"JSON report written to {out_path}")
    else:
        print(json.dumps(rep, indent=2))

    if args.submit:
        if not args.registry:
            print("--submit requires --registry URL", file=sys.stderr)
            return 1
        payload = build_payload(rep)
        key_path = os.environ.get("ATI_SUBMIT_SIGNING_KEY", "")
        if key_path and os.path.exists(key_path):
            with open(key_path, "rb") as kf:
                key_pem = kf.read()
            payload["signature"] = sign(payload, key_pem)
        else:
            print("Note: submission is unsigned (ATI_SUBMIT_SIGNING_KEY not set).", file=sys.stderr)
        result = submit(payload, args.registry)
        print("Submit result:", result)

    return 0


def _cmd_probes(args):
    probes = load_probes()
    for p in probes:
        print(f"  {p['id']:8s}  {p['category']:20s}  severity={p['severity']}  {p['input'][:60]}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ati-audit",
        description="AI Trust Index auditor — compute ATI locally, submit only scores.",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Generate example ati-audit.yaml")
    p_init.add_argument("-o", "--output", default="ati-audit.yaml")

    p_run = sub.add_parser("run", help="Run the audit")
    p_run.add_argument("-c", "--config", default="ati-audit.yaml")
    p_run.add_argument("--only", help="Score only this direction code (e.g. G11)")
    p_run.add_argument("--out", help="Output file (.json or .html)")
    p_run.add_argument("--self", action="store_true", dest="self_mode",
                       help="Local-only mode (default)")
    p_run.add_argument("--submit", action="store_true", help="Submit scores to registry")
    p_run.add_argument("--registry", help="Registry URL for --submit")

    p_probes = sub.add_parser("probes", help="Probe management")
    p_probes_sub = p_probes.add_subparsers(dest="probes_cmd")
    p_probes_sub.add_parser("list", help="List all probes")

    ns = parser.parse_args(argv)

    if ns.cmd == "init":
        return _cmd_init(ns)
    if ns.cmd == "run":
        return _cmd_run(ns)
    if ns.cmd == "probes":
        if ns.probes_cmd == "list":
            return _cmd_probes(ns)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
