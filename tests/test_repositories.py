import subprocess
from pathlib import Path

import pytest

from edge_catch.repositories import (
    normalize_commit,
    normalize_repository_source,
    temporary_repository,
)


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def make_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "original"
    repository.mkdir()
    git(repository, "init", "--quiet")
    git(repository, "config", "user.name", "Edge Catch Tests")
    git(repository, "config", "user.email", "tests@edge-catch.invalid")
    (repository / "value.txt").write_text("committed\n", encoding="utf-8")
    git(repository, "add", "value.txt")
    git(repository, "commit", "--quiet", "-m", "fixture")
    return repository, git(repository, "rev-parse", "HEAD")


def test_prepares_exact_commit_without_changing_original(tmp_path: Path) -> None:
    original, commit = make_repository(tmp_path)
    original_file = original / "value.txt"

    with temporary_repository(str(original), commit) as prepared:
        assert prepared.succeeded
        assert prepared.resolved_commit == commit
        assert len(prepared.commands) == 3
        assert prepared.workspace != original
        assert (prepared.workspace / "value.txt").read_text() == "committed\n"

        (prepared.workspace / "value.txt").write_text("candidate\n", encoding="utf-8")
        assert original_file.read_text(encoding="utf-8") == "committed\n"
        workspace = prepared.workspace

    assert not workspace.exists()
    assert original_file.read_text(encoding="utf-8") == "committed\n"


def test_preserves_failed_checkout_evidence(tmp_path: Path) -> None:
    original, _ = make_repository(tmp_path)
    missing_commit = "0" * 40

    with temporary_repository(str(original), missing_commit) as prepared:
        assert not prepared.succeeded
        assert prepared.error == "requested commit checkout failed"
        assert len(prepared.commands) == 2
        assert prepared.commands[0].succeeded
        assert not prepared.commands[1].succeeded


@pytest.mark.parametrize("commit", ["abc123", "g" * 40, ""])
def test_rejects_non_exact_commit(commit: str) -> None:
    with pytest.raises(ValueError, match="full 40-character"):
        normalize_commit(commit)


def test_normalizes_https_github_url() -> None:
    assert (
        normalize_repository_source("https://github.com/example/project")
        == "https://github.com/example/project.git"
    )


@pytest.mark.parametrize(
    "repository",
    [
        "http://github.com/example/project",
        "https://example.com/example/project",
        "https://github.com/example/project/issues",
        "https://github.com/example/project?token=secret",
    ],
)
def test_rejects_unsupported_repository_url(repository: str) -> None:
    with pytest.raises(ValueError, match="existing local directory or an HTTPS"):
        normalize_repository_source(repository)
