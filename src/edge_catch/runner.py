"""Run repository commands while preserving their observable evidence."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    """Evidence captured from one attempted command."""

    arguments: tuple[str, ...]
    working_directory: str
    return_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    launch_error: str | None

    @property
    def succeeded(self) -> bool:
        """Return whether the command launched, finished, and exited successfully."""
        return (
            self.launch_error is None
            and not self.timed_out
            and self.return_code == 0
        )


def run_command(
    arguments: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: float,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run one command without a shell and capture its result."""
    if not arguments:
        raise ValueError("arguments must not be empty")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    command = tuple(arguments)
    working_directory = str(cwd.resolve())
    started_at = time.monotonic()

    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            start_new_session=True,
        )
    except OSError as error:
        return CommandResult(
            arguments=command,
            working_directory=working_directory,
            return_code=None,
            stdout="",
            stderr="",
            duration_seconds=time.monotonic() - started_at,
            timed_out=False,
            launch_error=f"{type(error).__name__}: {error}",
        )

    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()

    return CommandResult(
        arguments=command,
        working_directory=working_directory,
        return_code=process.returncode,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=time.monotonic() - started_at,
        timed_out=timed_out,
        launch_error=None,
    )
