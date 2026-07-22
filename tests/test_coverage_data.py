import json
from pathlib import Path

import pytest

from edge_catch.coverage_data import (
    build_coverage_test_command,
    load_coverage_data,
)


def test_builds_branch_coverage_command_around_pytest() -> None:
    command = build_coverage_test_command(
        ("python", "-m", "pytest", "-q"),
        ("src/package",),
        "tests/test_candidate.py",
    )

    assert command == (
        "python",
        "-m",
        "coverage",
        "run",
        "--branch",
        "--source=src/package",
        "-m",
        "pytest",
        "-q",
        "tests/test_candidate.py",
    )


def test_loads_summary_and_file_gaps(tmp_path: Path) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(
        json.dumps(
            {
                "totals": {
                    "covered_lines": 8,
                    "num_statements": 10,
                    "covered_branches": 3,
                    "num_branches": 4,
                },
                "files": {
                    "src/package/module.py": {
                        "missing_lines": [12, 18],
                        "missing_branches": [[11, 12]],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    coverage = load_coverage_data(path)

    assert coverage.summary.covered_lines == 8
    file_coverage = coverage.for_file("src/package/module.py")
    assert file_coverage is not None
    assert file_coverage.missing_lines == (12, 18)
    assert file_coverage.missing_branches == ((11, 12),)


def test_rejects_malformed_coverage_json(tmp_path: Path) -> None:
    path = tmp_path / "coverage.json"
    path.write_text("not JSON", encoding="utf-8")

    with pytest.raises(ValueError, match="not valid JSON"):
        load_coverage_data(path)
