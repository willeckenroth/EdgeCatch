"""Prepare an exact repository commit in an independent temporary clone."""

from __future__ import annotations

import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from edge_catch.runner import CommandResult, run_command

_FULL_COMMIT = re.compile(r"[0-9a-fA-F]{40}")


@dataclass(frozen=True)
class PreparedRepository:
    """Evidence and workspace for one repository preparation attempt."""

    source: str
    requested_commit: str
    workspace: Path
    resolved_commit: str | None
    commands: tuple[CommandResult, ...]
    error: str | None

    @property
    def succeeded(self) -> bool:
        """Return whether the requested commit is ready in the workspace."""
        return self.error is None and self.resolved_commit == self.requested_commit


@contextmanager
def temporary_repository(
    repository: str,
    commit: str,
    *,
    timeout_seconds: float = 120,
) -> Iterator[PreparedRepository]:
    """Yield an independent checkout and remove it when the context exits."""
    source = normalize_repository_source(repository)
    requested_commit = normalize_commit(commit)

    with tempfile.TemporaryDirectory(prefix="edge-catch-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        workspace = temporary_root / "repository"
        commands: list[CommandResult] = []

        clone = run_command(
            [
                "git",
                "clone",
                "--no-hardlinks",
                "--no-checkout",
                "--quiet",
                source,
                str(workspace),
            ],
            cwd=temporary_root,
            timeout_seconds=timeout_seconds,
        )
        commands.append(clone)
        if not clone.succeeded:
            yield PreparedRepository(
                source=source,
                requested_commit=requested_commit,
                workspace=workspace,
                resolved_commit=None,
                commands=tuple(commands),
                error="repository clone failed",
            )
            return

        checkout = run_command(
            ["git", "checkout", "--detach", "--quiet", requested_commit],
            cwd=workspace,
            timeout_seconds=timeout_seconds,
        )
        commands.append(checkout)
        if not checkout.succeeded:
            yield PreparedRepository(
                source=source,
                requested_commit=requested_commit,
                workspace=workspace,
                resolved_commit=None,
                commands=tuple(commands),
                error="requested commit checkout failed",
            )
            return

        resolve = run_command(
            ["git", "rev-parse", "HEAD"],
            cwd=workspace,
            timeout_seconds=timeout_seconds,
        )
        commands.append(resolve)
        resolved_commit = resolve.stdout.strip().lower() if resolve.succeeded else None
        error = None
        if not resolve.succeeded:
            error = "checked-out commit could not be resolved"
        elif resolved_commit != requested_commit:
            error = "checked-out commit does not match the requested commit"

        yield PreparedRepository(
            source=source,
            requested_commit=requested_commit,
            workspace=workspace,
            resolved_commit=resolved_commit,
            commands=tuple(commands),
            error=error,
        )


def normalize_commit(commit: str) -> str:
    """Require a full hexadecimal commit identifier."""
    if _FULL_COMMIT.fullmatch(commit) is None:
        raise ValueError("commit must be a full 40-character hexadecimal identifier")
    return commit.lower()


def normalize_repository_source(repository: str) -> str:
    """Resolve a local directory or validate an HTTPS GitHub repository URL."""
    local_path = Path(repository)
    if local_path.exists():
        if not local_path.is_dir():
            raise ValueError("local repository must be a directory")
        return str(local_path.resolve())

    parsed = urlsplit(repository)
    parts = [part for part in parsed.path.split("/") if part]
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.query
        or parsed.fragment
        or len(parts) != 2
    ):
        raise ValueError(
            "repository must be an existing local directory or an HTTPS GitHub URL"
        )

    owner, name = parts
    if name.endswith(".git"):
        name = name[:-4]
    if not owner or not name or owner in {".", ".."} or name in {".", ".."}:
        raise ValueError("GitHub repository URL must contain an owner and name")
    return f"https://github.com/{owner}/{name}.git"
