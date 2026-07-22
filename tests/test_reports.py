import json
from pathlib import Path

from edge_catch.reports import (
    AnalysisReport,
    ProposalEvidence,
    RepositoryEvidence,
    write_reports,
)
from edge_catch.runner import CommandResult


def command_result() -> CommandResult:
    return CommandResult(
        arguments=("git", "rev-parse", "HEAD"),
        working_directory="/temporary/repository",
        return_code=0,
        stdout="a" * 40 + "\n",
        stderr="",
        duration_seconds=0.125,
        timed_out=False,
        launch_error=None,
    )


def test_writes_versioned_json_and_markdown(tmp_path: Path) -> None:
    commit = "a" * 40
    report = AnalysisReport(
        created_at_utc="2026-07-22T09:00:00Z",
        status="failed",
        repository=RepositoryEvidence(
            source="https://github.com/example/project.git",
            requested_commit=commit,
            resolved_commit=commit,
            commands=(command_result(),),
        ),
        baseline=None,
        target=None,
        proposal=ProposalEvidence(
            provider="recorded",
            model="fixture-model",
            prompt_version="walking-skeleton-v1",
            prompt="Return JSON.",
            raw_response="not JSON",
            parse_error="proposal is not valid JSON",
            proposal=None,
        ),
        validation=None,
        classification="environmental failure",
        human_review_status="unreviewed",
        error="baseline test command failed",
    )

    json_path, markdown_path = write_reports(report, tmp_path / "reports")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["repository"]["requested_commit"] == commit
    assert data["repository"]["commands"][0]["return_code"] == 0
    assert data["classification"] == "environmental failure"
    assert data["error"] == "baseline test command failed"

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# Edge Catch report" in markdown
    assert "**environmental failure**" in markdown
    assert "baseline test command failed" in markdown
    assert '["git", "rev-parse", "HEAD"]' in markdown
    assert "not JSON" in markdown
    assert "proposal is not valid JSON" in markdown
