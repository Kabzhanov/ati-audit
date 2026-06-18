# SPDX-License-Identifier: Apache-2.0
"""Registry of national AI/data-protection laws for G9 jurisdiction-aware scoring.

Add new countries by editing jurisdictions.yaml (ISO 3166-1 alpha-2 country codes).
Community PRs to extend the registry are welcome.
"""
import os
import yaml

_DEFAULT = os.path.join(os.path.dirname(__file__), "jurisdictions.yaml")


def load_jurisdictions(path=None) -> dict:
    """Return the jurisdictions mapping (dict keyed by country code).

    Args:
        path: Optional path to a custom jurisdictions YAML file.
              Defaults to the bundled ``ati_audit/jurisdictions.yaml``.

    Returns:
        dict mapping ISO 3166-1 alpha-2 country code → jurisdiction metadata.
    """
    with open(path or _DEFAULT, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("jurisdictions", {})
