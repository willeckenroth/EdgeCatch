"""Create the dedicated Python environment used for target commands."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import coverage

from edge_catch.runner import CommandResult, run_command


def create_target_environment(
    workspace: Path,
    *,
    timeout_seconds: float,
) -> tuple[tuple[CommandResult, ...], dict[str, str]]:
    """Create a target virtual environment and return its command environment."""
    environment_root = workspace.parent / "environment"
    creation = run_command(
        [
            sys.executable,
            "-m",
            "venv",
            str(environment_root),
        ],
        cwd=workspace.parent,
        timeout_seconds=timeout_seconds,
    )

    variables = dict(os.environ)
    variables["VIRTUAL_ENV"] = str(environment_root)
    variables["PATH"] = os.pathsep.join(
        [str(environment_root / "bin"), variables.get("PATH", "")]
    )
    variables.pop("PYTHONHOME", None)
    commands = [creation]
    if creation.succeeded:
        tooling = run_command(
            [
                str(environment_root / "bin" / "python"),
                "-m",
                "pip",
                "install",
                f"coverage=={coverage.__version__}",
            ],
            cwd=workspace.parent,
            timeout_seconds=timeout_seconds,
        )
        commands.append(tooling)
    return tuple(commands), variables
