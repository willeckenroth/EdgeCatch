"""Command-line entry point for Edge Catch."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from edge_catch import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="edge-catch",
        description=(
            "Propose and validate edge-case tests in trusted Python repositories."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Edge Catch command-line interface."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
