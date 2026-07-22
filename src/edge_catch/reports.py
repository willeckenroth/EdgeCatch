"""Versioned machine-readable and human-readable Edge Catch reports."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from edge_catch.proposals import Proposal
from edge_catch.runner import CommandResult
from edge_catch.targets import FunctionTarget

Classification = Literal[
    "unreviewed",
    "invalid generation",
    "environmental failure",
    "unsupported or ambiguous expectation",
    "redundant test",
    "validated regression candidate",
    "potential defect requiring human/maintainer confirmation",
]
REPORT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class RepositoryEvidence:
    """Repository identity and preparation command evidence."""

    source: str
    requested_commit: str
    resolved_commit: str | None
    commands: tuple[CommandResult, ...]


@dataclass(frozen=True)
class CoverageSummary:
    """Small deterministic summary of one coverage run."""

    covered_lines: int
    total_lines: int
    covered_branches: int
    total_branches: int


@dataclass(frozen=True)
class BaselineEvidence:
    """Installation, test, and coverage evidence before adding a candidate."""

    environment_commands: tuple[CommandResult, ...]
    installation_commands: tuple[CommandResult, ...]
    test_command: CommandResult | None
    coverage: CoverageSummary | None


@dataclass(frozen=True)
class ProposalEvidence:
    """Provenance and content of one unvalidated AI proposal."""

    provider: str
    model: str
    prompt_version: str
    prompt: str
    proposal: Proposal


@dataclass(frozen=True)
class ValidationEvidence:
    """Deterministic checks performed on one candidate test."""

    candidate_path: str
    parsed: bool
    parse_error: str | None
    collection_command: CommandResult | None
    candidate_command: CommandResult | None
    full_suite_command: CommandResult | None
    repeat_command: CommandResult | None
    coverage_after: CoverageSummary | None
    original_repository_unchanged: bool | None


@dataclass(frozen=True)
class AnalysisReport:
    """Source-of-truth evidence for one Edge Catch analysis attempt."""

    created_at_utc: str
    status: Literal["completed", "failed"]
    repository: RepositoryEvidence
    baseline: BaselineEvidence | None
    target: FunctionTarget | None
    proposal: ProposalEvidence | None
    validation: ValidationEvidence | None
    classification: Classification
    human_review_status: Literal["unreviewed", "accepted", "rejected"]
    error: str | None
    schema_version: int = field(default=REPORT_SCHEMA_VERSION, init=False)


def write_reports(report: AnalysisReport, output_directory: Path) -> tuple[Path, Path]:
    """Write report.json and its Markdown rendering."""
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / "report.json"
    markdown_path = output_directory / "report.md"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def render_markdown(report: AnalysisReport) -> str:
    """Render a concise human view of the machine-readable report."""
    lines = [
        "# Edge Catch report",
        "",
        f"- Schema version: `{report.schema_version}`",
        f"- Created at: `{report.created_at_utc}`",
        f"- Status: **{report.status}**",
        f"- Classification: **{report.classification}**",
        f"- Human review: **{report.human_review_status}**",
        "",
        "## Repository",
        "",
        f"- Source: `{report.repository.source}`",
        f"- Requested commit: `{report.repository.requested_commit}`",
        f"- Resolved commit: `{report.repository.resolved_commit or 'unavailable'}`",
    ]
    lines.extend(_render_commands("Preparation commands", report.repository.commands))

    if report.error is not None:
        lines.extend(["", "## Pipeline error", "", _indent(report.error)])

    if report.baseline is not None:
        lines.extend(["", "## Baseline"])
        lines.extend(
            _render_commands(
                "Environment commands",
                report.baseline.environment_commands,
            )
        )
        lines.extend(
            _render_commands(
                "Installation commands",
                report.baseline.installation_commands,
            )
        )
        if report.baseline.test_command is not None:
            lines.extend(
                _render_commands(
                    "Baseline test command",
                    (report.baseline.test_command,),
                )
            )
        if report.baseline.coverage is not None:
            coverage = report.baseline.coverage
            lines.extend(
                [
                    "",
                    "### Baseline coverage",
                    "",
                    f"- Lines: {coverage.covered_lines}/{coverage.total_lines}",
                    "- Branches: "
                    f"{coverage.covered_branches}/{coverage.total_branches}",
                ]
            )

    if report.target is not None:
        lines.extend(
            [
                "",
                "## Target",
                "",
                f"- File: `{report.target.source_path}`",
                f"- Function: `{report.target.qualified_name}`",
                f"- Lines: {report.target.start_line}-{report.target.end_line}",
                f"- Signature: `{report.target.signature}`",
                "",
                "### Exact source",
                "",
                _indent(report.target.source),
            ]
        )

    if report.proposal is not None:
        proposal = report.proposal
        lines.extend(
            [
                "",
                "## Unvalidated AI proposal",
                "",
                f"- Provider: `{proposal.provider}`",
                f"- Model: `{proposal.model}`",
                f"- Prompt version: `{proposal.prompt_version}`",
                f"- Hypothesis: {proposal.proposal.hypothesis}",
                f"- Expected behavior: {proposal.proposal.expected_behavior}",
                f"- Rationale: {proposal.proposal.rationale}",
                "",
                "### Assumptions",
                "",
                *(
                    f"- {assumption}"
                    for assumption in proposal.proposal.assumptions
                ),
                "",
                "### Prompt",
                "",
                _indent(proposal.prompt),
                "",
                "### Candidate test",
                "",
                _indent(proposal.proposal.test_code),
                "",
                "### Raw model response",
                "",
                _indent(proposal.proposal.raw_response),
            ]
        )

    if report.validation is not None:
        validation = report.validation
        lines.extend(
            [
                "",
                "## Deterministic validation",
                "",
                f"- Candidate path: `{validation.candidate_path}`",
                f"- Parsed: `{validation.parsed}`",
                f"- Parse error: `{validation.parse_error}`",
                "- Original repository unchanged: "
                f"`{validation.original_repository_unchanged}`",
            ]
        )
        for title, command in (
            ("Collection command", validation.collection_command),
            ("Candidate command", validation.candidate_command),
            ("Full-suite command", validation.full_suite_command),
            ("Repeat command", validation.repeat_command),
        ):
            if command is not None:
                lines.extend(_render_commands(title, (command,)))
        if validation.coverage_after is not None:
            coverage = validation.coverage_after
            lines.extend(
                [
                    "",
                    "### Coverage after candidate",
                    "",
                    f"- Lines: {coverage.covered_lines}/{coverage.total_lines}",
                    "- Branches: "
                    f"{coverage.covered_branches}/{coverage.total_branches}",
                ]
            )

    return "\n".join(lines) + "\n"


def _render_commands(title: str, commands: tuple[CommandResult, ...]) -> list[str]:
    lines = ["", f"### {title}", ""]
    if not commands:
        return [*lines, "None recorded."]

    for index, command in enumerate(commands, start=1):
        lines.extend(
            [
                f"#### Command {index}",
                "",
                "Arguments:",
                "",
                _indent(json.dumps(command.arguments)),
                "",
                f"- Working directory: `{command.working_directory}`",
                f"- Return code: `{command.return_code}`",
                f"- Timed out: `{command.timed_out}`",
                f"- Launch error: `{command.launch_error}`",
                f"- Duration: `{command.duration_seconds:.3f}` seconds",
                "",
                "Output:",
                "",
                _indent(command.stdout or "(no standard output)"),
                "",
                "Errors:",
                "",
                _indent(command.stderr or "(no standard error)"),
            ]
        )
    return lines


def _indent(text: str) -> str:
    return "\n".join(f"    {line}" for line in text.rstrip("\n").split("\n"))
