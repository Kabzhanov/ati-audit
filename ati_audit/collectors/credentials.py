# SPDX-License-Identifier: Apache-2.0
import os


def _read_pdf(path):
    try:
        from pypdf import PdfReader
        return "\n".join((pg.extract_text() or "") for pg in PdfReader(path).pages)
    except Exception:
        return ""


def read_credentials(path: str) -> list[dict]:
    out = []
    if not path or not os.path.isdir(path):
        return out
    for n in sorted(os.listdir(path)):
        fp = os.path.join(path, n)
        low = n.lower()
        if low.endswith((".txt", ".md")):
            out.append({"file": n, "text": open(fp, encoding="utf-8").read()})
        elif low.endswith(".pdf"):
            out.append({"file": n, "text": _read_pdf(fp)})
    return out
