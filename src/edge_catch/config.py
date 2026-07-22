"""Load the explicit commands Edge Catch may run for a repository."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePath


@dataclass(frozen=True)
class RepositoryConfig:
    """Repository-specific paths, commands, and timeout."""

    source_roots: tuple[str, ...]
    install_commands: tuple[tuple[str, ...], ...]
    test_command: tuple[str, ...]
    timeout_seconds: float


def load_repository_config(path: Path) -> RepositoryConfig:
    """Load and validate a repository configuration from TOML."""
    with path.open("rb") as file:
        data = tomllib.load(file)

    repository = _require_table(data, "repository")
    commands = _require_table(data, "commands")

    source_roots = _require_relative_paths(
        repository.get("source_roots"),
        "repository.source_roots",
    )
    install_commands = _require_command_list(
        commands.get("install", []),
        "commands.install",
    )
    test_command = _require_command(commands.get("test"), "commands.test")
    if test_command[:3] != ("python", "-m", "pytest"):
        raise ValueError("commands.test must begin with ['python', '-m', 'pytest']")
    timeout_seconds = _require_positive_number(
        commands.get("timeout_seconds", 120),
        "commands.timeout_seconds",
    )

    return RepositoryConfig(
        source_roots=source_roots,
        install_commands=install_commands,
        test_command=test_command,
        timeout_seconds=timeout_seconds,
    )


def _require_table(data: dict[str, object], name: str) -> dict[str, object]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a TOML table")
    return value


def _require_relative_paths(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty array of relative paths")

    paths: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{name} must contain only non-empty strings")
        path = PurePath(item)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"{name} must contain only paths inside the repository")
        paths.append(item)
    return tuple(paths)


def _require_command(value: object, name: str) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(argument, str) and argument for argument in value)
    ):
        raise ValueError(f"{name} must be a non-empty array of arguments")
    return tuple(value)


def _require_command_list(
    value: object,
    name: str,
) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array of command arrays")
    return tuple(
        _require_command(command, f"{name}[{index}]")
        for index, command in enumerate(value)
    )


def _require_positive_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
    return float(value)
