"""Deterministically validate one recorded candidate test."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path

from edge_catch.config import RepositoryConfig
from edge_catch.coverage_data import (
    COVERAGE_JSON_PATH,
    build_coverage_test_command,
    coverage_report_command,
    load_coverage_data,
)
from edge_catch.reports import Classification, ValidationEvidence
from edge_catch.runner import run_command


def validate_candidate(
    test_code: str,
    workspace: Path,
    config: RepositoryConfig,
    environment: Mapping[str, str],
) -> ValidationEvidence:
    """Parse and run a candidate only inside the temporary repository."""
    candidate_path = _candidate_path(workspace)
    relative_candidate = str(candidate_path.relative_to(workspace))
    try:
        ast.parse(test_code, filename=relative_candidate)
    except SyntaxError as error:
        return ValidationEvidence(
            candidate_path=relative_candidate,
            parsed=False,
            parse_error=f"{error.msg} at line {error.lineno}",
            collection_command=None,
            candidate_command=None,
            full_suite_command=None,
            coverage_report_command=None,
            repeat_command=None,
            coverage_after=None,
            coverage_error=None,
            original_repository_unchanged=True,
        )

    candidate_path.write_text(test_code, encoding="utf-8")
    collection = run_command(
        (*config.test_command, "--collect-only", relative_candidate),
        cwd=workspace,
        timeout_seconds=config.timeout_seconds,
        env=environment,
    )
    candidate = None
    full_suite = None
    repeat = None
    if collection.succeeded:
        candidate = run_command(
            build_coverage_test_command(
                config.test_command,
                config.source_roots,
                relative_candidate,
            ),
            cwd=workspace,
            timeout_seconds=config.timeout_seconds,
            env=environment,
        )
    if candidate is not None and candidate.succeeded:
        full_suite = run_command(
            build_coverage_test_command(
                config.test_command,
                config.source_roots,
            ),
            cwd=workspace,
            timeout_seconds=config.timeout_seconds,
            env=environment,
        )
    report = None
    coverage = None
    coverage_error = None
    if full_suite is not None and full_suite.succeeded:
        report = run_command(
            coverage_report_command(),
            cwd=workspace,
            timeout_seconds=config.timeout_seconds,
            env=environment,
        )
        if report.succeeded:
            try:
                coverage = load_coverage_data(workspace / COVERAGE_JSON_PATH).summary
            except (OSError, ValueError) as error:
                coverage_error = f"{type(error).__name__}: {error}"
    if report is not None and report.succeeded and coverage_error is None:
        repeat = run_command(
            (*config.test_command, relative_candidate),
            cwd=workspace,
            timeout_seconds=config.timeout_seconds,
            env=environment,
        )

    return ValidationEvidence(
        candidate_path=relative_candidate,
        parsed=True,
        parse_error=None,
        collection_command=collection,
        candidate_command=candidate,
        full_suite_command=full_suite,
        coverage_report_command=report,
        repeat_command=repeat,
        coverage_after=coverage,
        coverage_error=coverage_error,
        original_repository_unchanged=True,
    )


def classify_validation(validation: ValidationEvidence) -> Classification:
    """Classify only objective structural or environmental outcomes."""
    if not validation.parsed:
        return "invalid generation"

    commands = (
        validation.collection_command,
        validation.candidate_command,
        validation.full_suite_command,
        validation.coverage_report_command,
        validation.repeat_command,
    )
    if any(
        command is not None and (command.timed_out or command.launch_error is not None)
        for command in commands
    ):
        return "environmental failure"
    if validation.coverage_error is not None:
        return "environmental failure"
    if (
        validation.coverage_report_command is not None
        and not validation.coverage_report_command.succeeded
    ):
        return "environmental failure"
    if (
        validation.collection_command is not None
        and not validation.collection_command.succeeded
    ):
        return "invalid generation"
    return "unreviewed"


def _candidate_path(workspace: Path) -> Path:
    resolved_workspace = workspace.resolve()
    tests_directory = workspace / "tests"
    parent = tests_directory if tests_directory.is_dir() else workspace
    if not parent.resolve().is_relative_to(resolved_workspace):
        parent = workspace

    candidate = parent / "test_edge_catch_candidate.py"
    if candidate.exists():
        relative_candidate = candidate.relative_to(workspace)
        raise ValueError(f"candidate path already exists: {relative_candidate}")
    return candidate
