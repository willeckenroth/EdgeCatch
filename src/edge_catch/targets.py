"""Extract explicitly selected Python functions from source files."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FunctionTarget:
    """Source evidence for one named function or method."""

    source_path: str
    qualified_name: str
    start_line: int
    end_line: int
    signature: str
    docstring: str | None
    source: str


class _FunctionFinder(ast.NodeVisitor):
    """Find function definitions while tracking their lexical names."""

    def __init__(self, qualified_name: str) -> None:
        self.qualified_name = qualified_name
        self.scope: list[str] = []
        self.matches: list[ast.FunctionDef | ast.AsyncFunctionDef] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        name = ".".join([*self.scope, node.name])
        if name == self.qualified_name:
            self.matches.append(node)

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()


def extract_function(source_path: Path, qualified_name: str) -> FunctionTarget:
    """Return the exact source evidence for one qualified function name."""
    if not qualified_name or any(
        not part.isidentifier() for part in qualified_name.split(".")
    ):
        raise ValueError("qualified_name must contain valid dotted Python names")

    text = source_path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(source_path))
    finder = _FunctionFinder(qualified_name)
    finder.visit(tree)

    if not finder.matches:
        raise ValueError(f"function not found: {qualified_name}")
    if len(finder.matches) > 1:
        raise ValueError(f"function name is ambiguous: {qualified_name}")

    node = finder.matches[0]
    start_line = min(
        [node.lineno, *(decorator.lineno for decorator in node.decorator_list)]
    )
    end_line = node.end_lineno
    if end_line is None:
        raise ValueError(f"function has no source boundary: {qualified_name}")

    lines = text.splitlines(keepends=True)
    return FunctionTarget(
        source_path=str(source_path),
        qualified_name=qualified_name,
        start_line=start_line,
        end_line=end_line,
        signature=_format_signature(node),
        docstring=ast.get_docstring(node, clean=False),
        source="".join(lines[start_line - 1 : end_line]),
    )


def _format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    signature = f"{prefix} {node.name}({ast.unparse(node.args)})"
    if node.returns is not None:
        signature += f" -> {ast.unparse(node.returns)}"
    return signature
