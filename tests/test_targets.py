from pathlib import Path

import pytest

from edge_catch.targets import extract_function


def write_source(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "example.py"
    path.write_text(text, encoding="utf-8")
    return path


def test_extracts_decorated_function_boundaries(tmp_path: Path) -> None:
    path = write_source(
        tmp_path,
        '''CONSTANT = 1

@decorator
def format_value(value: int, prefix: str = "") -> str:
    """Format one value."""
    return f"{prefix}{value}"

OTHER = 2
''',
    )

    target = extract_function(path, "format_value")

    assert target.start_line == 3
    assert target.end_line == 6
    assert target.signature == "def format_value(value: int, prefix: str='') -> str"
    assert target.docstring == "Format one value."
    assert target.source == '''@decorator
def format_value(value: int, prefix: str = "") -> str:
    """Format one value."""
    return f"{prefix}{value}"
'''


def test_extracts_qualified_async_method(tmp_path: Path) -> None:
    path = write_source(
        tmp_path,
        '''class Client:
    async def fetch(self, key: str) -> bytes:
        return key.encode()
''',
    )

    target = extract_function(path, "Client.fetch")

    assert target.qualified_name == "Client.fetch"
    assert target.signature == "async def fetch(self, key: str) -> bytes"


def test_rejects_missing_function(tmp_path: Path) -> None:
    path = write_source(tmp_path, "def present():\n    return True\n")

    with pytest.raises(ValueError, match="function not found: missing"):
        extract_function(path, "missing")


def test_rejects_invalid_qualified_name(tmp_path: Path) -> None:
    path = write_source(tmp_path, "def present():\n    return True\n")

    with pytest.raises(ValueError, match="valid dotted Python names"):
        extract_function(path, "present..child")


def test_rejects_ambiguous_function_name(tmp_path: Path) -> None:
    path = write_source(
        tmp_path,
        '''if condition:
    def duplicate():
        return 1
else:
    def duplicate():
        return 2
''',
    )

    with pytest.raises(ValueError, match="function name is ambiguous"):
        extract_function(path, "duplicate")
