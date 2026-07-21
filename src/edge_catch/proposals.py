"""Parse structured AI proposals without treating them as validated tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Proposal:
    """One unvalidated edge-case hypothesis and candidate test."""

    hypothesis: str
    assumptions: tuple[str, ...]
    expected_behavior: str
    rationale: str
    test_name: str
    test_code: str
    raw_response: str


_REQUIRED_FIELDS = {
    "hypothesis",
    "assumptions",
    "expected_behavior",
    "rationale",
    "test_name",
    "test_code",
}


def load_proposal(path: Path) -> Proposal:
    """Load a recorded model response from a UTF-8 JSON file."""
    return parse_proposal(path.read_text(encoding="utf-8"))


def parse_proposal(raw_response: str) -> Proposal:
    """Validate the exact JSON shape required from the proposal stage."""
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise ValueError(f"proposal is not valid JSON: {error.msg}") from error

    if not isinstance(data, dict):
        raise ValueError("proposal must be a JSON object")

    fields = set(data)
    missing = _REQUIRED_FIELDS - fields
    extra = fields - _REQUIRED_FIELDS
    if missing:
        raise ValueError(f"proposal is missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"proposal has unexpected fields: {', '.join(sorted(extra))}")

    assumptions = data["assumptions"]
    if not isinstance(assumptions, list) or not all(
        isinstance(assumption, str) and assumption.strip()
        for assumption in assumptions
    ):
        raise ValueError("proposal assumptions must be an array of non-empty strings")

    string_fields = _REQUIRED_FIELDS - {"assumptions"}
    for field in sorted(string_fields):
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"proposal {field} must be a non-empty string")

    return Proposal(
        hypothesis=data["hypothesis"],
        assumptions=tuple(assumptions),
        expected_behavior=data["expected_behavior"],
        rationale=data["rationale"],
        test_name=data["test_name"],
        test_code=data["test_code"],
        raw_response=raw_response,
    )
