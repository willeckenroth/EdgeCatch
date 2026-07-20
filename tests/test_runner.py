import signal
import sys
from pathlib import Path

from edge_catch.runner import run_command


def test_captures_successful_command_output(tmp_path: Path) -> None:
    result = run_command(
        [sys.executable, "-c", "print('command output')"],
        cwd=tmp_path,
        timeout_seconds=1,
    )

    assert result.succeeded
    assert result.return_code == 0
    assert result.stdout == "command output\n"
    assert result.stderr == ""
    assert not result.timed_out
    assert result.launch_error is None


def test_preserves_nonzero_exit_as_evidence(tmp_path: Path) -> None:
    result = run_command(
        [
            sys.executable,
            "-c",
            "import sys; print('failure', file=sys.stderr); raise SystemExit(7)",
        ],
        cwd=tmp_path,
        timeout_seconds=1,
    )

    assert not result.succeeded
    assert result.return_code == 7
    assert result.stderr == "failure\n"
    assert not result.timed_out
    assert result.launch_error is None


def test_kills_timed_out_process_group(tmp_path: Path) -> None:
    result = run_command(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        timeout_seconds=0.05,
    )

    assert not result.succeeded
    assert result.return_code == -signal.SIGKILL
    assert result.timed_out
    assert result.launch_error is None
    assert result.duration_seconds < 1


def test_preserves_launch_error(tmp_path: Path) -> None:
    result = run_command(
        ["edge-catch-command-that-does-not-exist"],
        cwd=tmp_path,
        timeout_seconds=1,
    )

    assert not result.succeeded
    assert result.return_code is None
    assert result.launch_error is not None
    assert result.launch_error.startswith("FileNotFoundError:")
