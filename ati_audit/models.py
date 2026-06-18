# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass, field


@dataclass
class Evidence:
    category: str
    snippet: str
    source: str


@dataclass
class ScoreResult:
    code: str
    score: int | None
    active: bool
    applicable: bool
    rationale: str
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class ProbeResult:
    id: str
    category: str
    severity: int
    passed: bool
    detail: str
