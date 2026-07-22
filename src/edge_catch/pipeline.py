"""Compose the deterministic recorded-proposal walking skeleton."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path, PurePath
from typing import Literal

from edge_catch.config import RepositoryConfig, load_repository_config
from edge_catch.prompts import PROMPT_VERSION, build_proposal_prompt
from edge_catch.proposals import parse_proposal
from edge_catch.reports import (
    AnalysisReport,
    BaselineEvidence,
    Classification,
    ProposalEvidence,
    RepositoryEvidence,
    ValidationEvidence,
)
from edge_catch.repositories import PreparedRepository, temporary_repository
from edge_catch.runner import CommandResult, run_command
from edge_catch.targets import FunctionTarget, extract_function
from edge_catch.validation import classify_validation, validate_candidate


@dataclass(frozen=True)
class RecordedAnalysisRequest:
    """Inputs for a deterministic analysis using a preserved model response."""

    repository: str
    commit: str
    config_path: Path
    target_file: str
    target_qualified_name: str
    proposal_path: Path
    model: str
    provider: str = "recorded"
    created_at_utc: str | None = None


def analyze_recorded(request: RecordedAnalysisRequest) -> AnalysisReport:
    """Run the recorded-proposal pipeline and return all collected evidence."""
    config = load_repository_config(request.config_path)
    created_at = request.created_at_utc or _current_utc_time()

    with temporary_repository(
        request.repository,
        request.commit,
        timeout_seconds=config.timeout_seconds,
    ) as prepared:
        repository = _repository_evidence(prepared)
        if not prepared.succeeded:
            return _report(
                created_at=created_at,
                status="failed",
                repository=repository,
                classification="environmental failure",
                error=prepared.error,
            )

        installation_commands = _run_installation_commands(config, prepared.workspace)
        baseline = BaselineEvidence(
            environment_commands=(),
            installation_commands=installation_commands,
            test_command=None,
            coverage=None,
        )
        failed_installation = next(
            (command for command in installation_commands if not command.succeeded),
            None,
        )
        if failed_installation is not None:
            return _report(
                created_at=created_at,
                status="failed",
                repository=repository,
                baseline=baseline,
                classification="environmental failure",
                error="repository installation command failed",
            )

        baseline_command = run_command(
            config.test_command,
            cwd=prepared.workspace,
            timeout_seconds=config.timeout_seconds,
        )
        baseline = replace(baseline, test_command=baseline_command)
        if not baseline_command.succeeded:
            return _report(
                created_at=created_at,
                status="failed",
                repository=repository,
                baseline=baseline,
                classification="environmental failure",
                error="baseline test command failed",
            )

        try:
            source_path = _path_inside_repository(
                prepared.workspace,
                request.target_file,
            )
            target = extract_function(source_path, request.target_qualified_name)
        except (OSError, SyntaxError, ValueError) as error:
            return _report(
                created_at=created_at,
                status="failed",
                repository=repository,
                baseline=baseline,
                error=f"target extraction failed: {type(error).__name__}: {error}",
            )
        target = replace(target, source_path=request.target_file)

        prompt = build_proposal_prompt(target)
        proposal_evidence = _load_proposal_evidence(request, prompt)
        if proposal_evidence.proposal is None:
            return _report(
                created_at=created_at,
                status="completed",
                repository=repository,
                baseline=baseline,
                target=target,
                proposal=proposal_evidence,
                classification="invalid generation",
            )

        try:
            validation = validate_candidate(
                proposal_evidence.proposal.test_code,
                prepared.workspace,
                config,
            )
        except (OSError, ValueError) as error:
            return _report(
                created_at=created_at,
                status="failed",
                repository=repository,
                baseline=baseline,
                target=target,
                proposal=proposal_evidence,
                error=f"candidate preparation failed: {type(error).__name__}: {error}",
            )
        return _report(
            created_at=created_at,
            status="completed",
            repository=repository,
            baseline=baseline,
            target=target,
            proposal=proposal_evidence,
            validation=validation,
            classification=classify_validation(validation),
        )


def _run_installation_commands(
    config: RepositoryConfig,
    workspace: Path,
) -> tuple[CommandResult, ...]:
    results: list[CommandResult] = []
    for command in config.install_commands:
        result = run_command(
            command,
            cwd=workspace,
            timeout_seconds=config.timeout_seconds,
        )
        results.append(result)
        if not result.succeeded:
            break
    return tuple(results)


def _load_proposal_evidence(
    request: RecordedAnalysisRequest,
    prompt: str,
) -> ProposalEvidence:
    try:
        raw_response = request.proposal_path.read_text(encoding="utf-8")
    except OSError as error:
        return ProposalEvidence(
            provider=request.provider,
            model=request.model,
            prompt_version=PROMPT_VERSION,
            prompt=prompt,
            raw_response="",
            parse_error=f"{type(error).__name__}: {error}",
            proposal=None,
        )

    try:
        proposal = parse_proposal(raw_response)
    except ValueError as error:
        return ProposalEvidence(
            provider=request.provider,
            model=request.model,
            prompt_version=PROMPT_VERSION,
            prompt=prompt,
            raw_response=raw_response,
            parse_error=str(error),
            proposal=None,
        )

    return ProposalEvidence(
        provider=request.provider,
        model=request.model,
        prompt_version=PROMPT_VERSION,
        prompt=prompt,
        raw_response=raw_response,
        parse_error=None,
        proposal=proposal,
    )


def _path_inside_repository(workspace: Path, relative_path: str) -> Path:
    path = PurePath(relative_path)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("target file must be a relative path inside the repository")

    resolved_workspace = workspace.resolve()
    resolved_path = (workspace / path).resolve()
    if not resolved_path.is_relative_to(resolved_workspace):
        raise ValueError("target file resolves outside the repository")
    if not resolved_path.is_file():
        raise ValueError(f"target file does not exist: {relative_path}")
    return resolved_path


def _repository_evidence(prepared: PreparedRepository) -> RepositoryEvidence:
    return RepositoryEvidence(
        source=prepared.source,
        requested_commit=prepared.requested_commit,
        resolved_commit=prepared.resolved_commit,
        commands=prepared.commands,
    )


def _report(
    *,
    created_at: str,
    status: Literal["completed", "failed"],
    repository: RepositoryEvidence,
    baseline: BaselineEvidence | None = None,
    target: FunctionTarget | None = None,
    proposal: ProposalEvidence | None = None,
    validation: ValidationEvidence | None = None,
    classification: Classification = "unreviewed",
    error: str | None = None,
) -> AnalysisReport:
    return AnalysisReport(
        created_at_utc=created_at,
        status=status,
        repository=repository,
        baseline=baseline,
        target=target,
        proposal=proposal,
        validation=validation,
        classification=classification,
        human_review_status="unreviewed",
        error=error,
    )


def _current_utc_time() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )
