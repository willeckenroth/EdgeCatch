import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from edge_catch.cli import main
from edge_catch.pipeline import RecordedAnalysisRequest, analyze_recorded
from edge_catch.reports import write_reports


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def make_fixture_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "fixture-repository"
    tests = repository / "tests"
    tests.mkdir(parents=True)
    (repository / "sample.py").write_text(
        "def is_positive(value: int) -> bool:\n    return value > 0\n",
        encoding="utf-8",
    )
    (tests / "test_sample.py").write_text(
        "from sample import is_positive\n\n"
        "def test_positive_value():\n    assert is_positive(1) is True\n",
        encoding="utf-8",
    )
    git(repository, "init", "--quiet")
    git(repository, "config", "user.name", "Edge Catch Tests")
    git(repository, "config", "user.email", "tests@edge-catch.invalid")
    git(repository, "add", ".")
    git(repository, "commit", "--quiet", "-m", "fixture")
    return repository, git(repository, "rev-parse", "HEAD")


def write_config(tmp_path: Path) -> Path:
    config = tmp_path / "repository.toml"
    config.write_text(
        '''[repository]
source_roots = ["."]

[commands]
test = ["python", "-m", "pytest", "-q"]
timeout_seconds = 10
''',
        encoding="utf-8",
    )
    return config


def write_proposal(tmp_path: Path, test_code: str) -> Path:
    path = tmp_path / "proposal.json"
    path.write_text(
        json.dumps(
            {
                "hypothesis": "Zero exercises the boundary of positive values.",
                "assumptions": ["Zero is not considered positive."],
                "expected_behavior": "The function returns False for zero.",
                "rationale": "The existing test only uses a positive integer.",
                "test_name": "test_zero_is_not_positive",
                "test_code": test_code,
            }
        ),
        encoding="utf-8",
    )
    return path


def request(
    repository: Path,
    commit: str,
    config: Path,
    proposal: Path,
) -> RecordedAnalysisRequest:
    return RecordedAnalysisRequest(
        repository=str(repository),
        commit=commit,
        config_path=config,
        target_file="sample.py",
        target_qualified_name="is_positive",
        proposal_path=proposal,
        model="fixture-model",
        created_at_utc="2026-07-22T09:00:00Z",
    )


def current_test_environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment["PATH"] = os.pathsep.join(
        [str(Path(sys.executable).parent), environment.get("PATH", "")]
    )
    return environment


def test_recorded_pipeline_runs_end_to_end_and_preserves_original(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository, commit = make_fixture_repository(tmp_path)
    config = write_config(tmp_path)
    proposal = write_proposal(
        tmp_path,
        "from sample import is_positive\n\n"
        "def test_zero_is_not_positive():\n"
        "    assert is_positive(0) is False\n",
    )

    report = analyze_recorded(
        request(repository, commit, config, proposal),
        existing_environment=current_test_environment(),
    )
    json_path, _ = write_reports(report, tmp_path / "output")

    assert report.status == "completed", report
    assert report.classification == "unreviewed"
    assert report.baseline is not None
    assert report.baseline.test_command is not None
    assert report.baseline.test_command.succeeded
    assert report.baseline.coverage_report_command is not None
    assert report.baseline.coverage_report_command.succeeded
    assert report.baseline.coverage is not None
    assert report.target is not None
    assert report.target.qualified_name == "is_positive"
    assert report.proposal is not None
    assert report.proposal.parse_error is None
    assert "Missing lines inside target:" in report.proposal.prompt
    assert report.validation is not None
    assert report.validation.parsed
    assert report.validation.collection_command is not None
    assert report.validation.collection_command.succeeded
    assert report.validation.candidate_command is not None
    assert report.validation.candidate_command.succeeded
    assert report.validation.full_suite_command is not None
    assert report.validation.full_suite_command.succeeded
    assert report.validation.coverage_report_command is not None
    assert report.validation.coverage_report_command.succeeded
    assert report.validation.coverage_after is not None
    assert report.validation.repeat_command is not None
    assert report.validation.repeat_command.succeeded
    assert not (repository / "tests" / "test_edge_catch_candidate.py").exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["repository"]["resolved_commit"] == commit
    assert data["validation"]["candidate_path"] == (
        "tests/test_edge_catch_candidate.py"
    )

    cli_output = tmp_path / "cli-output"
    monkeypatch.setattr(
        "edge_catch.cli.analyze_recorded",
        lambda cli_request: analyze_recorded(
            cli_request,
            existing_environment=current_test_environment(),
        ),
    )
    assert (
        main(
            [
                "analyze",
                str(repository),
                "--commit",
                commit,
                "--config",
                str(config),
                "--output",
                str(cli_output),
                "--target",
                "sample.py:is_positive",
                "--proposal",
                str(proposal),
                "--model",
                "fixture-model",
            ]
        )
        == 0
    )
    assert (cli_output / "report.json").is_file()
    assert "JSON report:" in capsys.readouterr().out


def test_pipeline_reports_invalid_candidate_syntax(tmp_path: Path) -> None:
    repository, commit = make_fixture_repository(tmp_path)
    config = write_config(tmp_path)
    proposal = write_proposal(tmp_path, "def broken(:\n    pass\n")

    report = analyze_recorded(
        request(repository, commit, config, proposal),
        existing_environment=current_test_environment(),
    )

    assert report.status == "completed", report
    assert report.classification == "invalid generation"
    assert report.validation is not None
    assert not report.validation.parsed
    assert report.validation.parse_error is not None
    assert report.validation.collection_command is None
    assert not (repository / "tests" / "test_edge_catch_candidate.py").exists()


def test_pipeline_preserves_malformed_model_response(tmp_path: Path) -> None:
    repository, commit = make_fixture_repository(tmp_path)
    config = write_config(tmp_path)
    proposal = tmp_path / "malformed.json"
    proposal.write_text("not JSON", encoding="utf-8")

    report = analyze_recorded(
        request(repository, commit, config, proposal),
        existing_environment=current_test_environment(),
    )

    assert report.status == "completed", report
    assert report.classification == "invalid generation"
    assert report.proposal is not None
    assert report.proposal.raw_response == "not JSON"
    assert report.proposal.parse_error is not None
    assert report.proposal.proposal is None
    assert report.validation is None
