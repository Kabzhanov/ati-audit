# SPDX-License-Identifier: Apache-2.0
import os

_KEYS = {
    "policy": ("policy", "политик"),
    "registry": ("registry", "реестр"),
    "risk": ("risk", "риск"),
    "process": ("process", "процесс", "governance"),
    "roadmap": ("roadmap", "дорожн"),
}


def scan_docs(docs_path: str) -> dict:
    files = {}
    if docs_path and os.path.isdir(docs_path):
        for root, _, names in os.walk(docs_path):
            for n in names:
                if n.lower().endswith((".md", ".txt", ".rst")):
                    try:
                        files[n] = open(os.path.join(root, n), encoding="utf-8").read()
                    except OSError:
                        pass
    blob = " ".join((k + " " + v) for k, v in files.items()).lower()
    found = {key: any(t in blob for t in terms) for key, terms in _KEYS.items()}
    return {"files": files, "found": found}
