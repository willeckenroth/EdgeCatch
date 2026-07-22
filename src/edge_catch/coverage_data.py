"""Build coverage commands and parse their versioned JSON evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from edge_catch.reports import CoverageSummary

COVERAGE_JSON_PATH = ".edge-catch-coverage.json"


@dataclass(frozen=True)
class FileCoverage:
    """Missing line and branch evidence for one source file."""

    path: str
    missing_lines: tuple[int, ...]
    missing_branches: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class CoverageData:
    """Coverage summary and per-file gaps parsed from coverage.py JSON."""

    summary: CoverageSummary
    files: tuple[FileCoverage, ...]

    def for_file(self, path: str) -> FileCoverage | None:
        """Find file coverage using normalized repository-relative paths."""
        normalized = str(PurePosixPath(path))
        return next((file for file in self.files if file.path == normalized), None)


def build_coverage_test_command(
    test_command: tuple[str, ...],
    source_roots: tuple[str, ...],
    *extra_pytest_arguments: str,
) -> tuple[str, ...]:
    """Wrap the configured pytest arguments in branch coverage."""
    if test_command[:3] != ("python", "-m", "pytest"):
        raise ValueError("test command must begin with python -m pytest")
    sources = tuple(f"--source={source}" for source in source_roots)
    return (
        "python",
        "-m",
        "coverage",
        "run",
        "--branch",
        *sources,
        "-m",
        "pytest",
        *test_command[3:],
        *extra_pytest_arguments,
    )


def coverage_report_command() -> tuple[str, ...]:
    """Return the fixed command that exports coverage JSON."""
    return (
        "python",
        "-m",
        "coverage",
        "json",
        "-o",
        COVERAGE_JSON_PATH,
    )


def load_coverage_data(path: Path) -> CoverageData:
    """Load the totals and missing locations from coverage.py JSON."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"coverage report is not valid JSON: {error.msg}") from error

    if not isinstance(data, dict):
        raise ValueError("coverage report must be a JSON object")
    totals = _require_object(data.get("totals"), "coverage totals")
    files = _require_object(data.get("files"), "coverage files")

    summary = CoverageSummary(
        covered_lines=_require_integer(totals, "covered_lines"),
        total_lines=_require_integer(totals, "num_statements"),
        covered_branches=_require_integer(totals, "covered_branches"),
        total_branches=_require_integer(totals, "num_branches"),
    )
    file_coverage = tuple(
        _parse_file_coverage(file_path, value)
        for file_path, value in sorted(files.items())
    )
    return CoverageData(summary=summary, files=file_coverage)


def _parse_file_coverage(path: str, value: object) -> FileCoverage:
    if not isinstance(path, str):
        raise ValueError("coverage file paths must be strings")
    file_data = _require_object(value, f"coverage file {path}")
    missing_lines = _require_integer_list(file_data, "missing_lines")
    raw_branches = file_data.get("missing_branches")
    if not isinstance(raw_branches, list):
        raise ValueError(f"coverage file {path} missing_branches must be an array")

    branches: list[tuple[int, int]] = []
    for branch in raw_branches:
        if (
            not isinstance(branch, list)
            or len(branch) != 2
            or not all(
                isinstance(line, int) and not isinstance(line, bool)
                for line in branch
            )
        ):
            raise ValueError(f"coverage file {path} has an invalid missing branch")
        branches.append((branch[0], branch[1]))

    return FileCoverage(
        path=str(PurePosixPath(path)),
        missing_lines=tuple(missing_lines),
        missing_branches=tuple(branches),
    )


def _require_object(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _require_integer(data: dict[str, object], name: str) -> int:
    value = data.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"coverage {name} must be a non-negative integer")
    return value


def _require_integer_list(data: dict[str, object], name: str) -> list[int]:
    value = data.get(name)
    if not isinstance(value, list) or not all(
        isinstance(item, int) and not isinstance(item, bool) and item > 0
        for item in value
    ):
        raise ValueError(f"coverage {name} must be an array of positive integers")
    return value
