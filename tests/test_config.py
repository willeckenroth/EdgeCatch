from pathlib import Path

import pytest

from edge_catch.config import RepositoryConfig, load_repository_config


def write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "repository.toml"
    path.write_text(text)
    return path


def test_loads_explicit_commands(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
[repository]
source_roots = ["src", "lib"]

[commands]
install = [
    ["python", "-m", "pip", "install", "-e", ".[tests]"],
]
test = ["python", "-m", "pytest", "-q"]
timeout_seconds = 45
""",
    )

    assert load_repository_config(path) == RepositoryConfig(
        source_roots=("src", "lib"),
        install_commands=(
            ("python", "-m", "pip", "install", "-e", ".[tests]"),
        ),
        test_command=("python", "-m", "pytest", "-q"),
        timeout_seconds=45.0,
    )


def test_rejects_a_shell_command_string(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
[repository]
source_roots = ["src"]

[commands]
test = "pytest -q"
""",
    )

    with pytest.raises(ValueError, match="commands.test"):
        load_repository_config(path)


@pytest.mark.parametrize("source_root", ["/tmp/source", "../source"])
def test_rejects_source_roots_outside_repository(
    tmp_path: Path,
    source_root: str,
) -> None:
    path = write_config(
        tmp_path,
        f"""
[repository]
source_roots = ["{source_root}"]

[commands]
test = ["python", "-m", "pytest"]
""",
    )

    with pytest.raises(ValueError, match="inside the repository"):
        load_repository_config(path)


def test_rejects_non_positive_timeout(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
[repository]
source_roots = ["src"]

[commands]
test = ["python", "-m", "pytest"]
timeout_seconds = 0
""",
    )

    with pytest.raises(ValueError, match="positive number"):
        load_repository_config(path)
