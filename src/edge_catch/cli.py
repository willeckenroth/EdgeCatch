"""Command-line entry point for Edge Catch."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from edge_catch import __version__
from edge_catch.pipeline import RecordedAnalysisRequest, analyze_recorded
from edge_catch.reports import write_reports


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
    subparsers = parser.add_subparsers(dest="command")
    analyze = subparsers.add_parser(
        "analyze",
        help="analyze one exact repository commit",
    )
    analyze.add_argument("repository", help="local path or HTTPS GitHub URL")
    analyze.add_argument("--commit", required=True, help="full 40-character commit")
    analyze.add_argument("--config", required=True, type=Path)
    analyze.add_argument("--output", required=True, type=Path)
    analyze.add_argument(
        "--target",
        required=True,
        metavar="FILE:QUALNAME",
        help="explicit walking-skeleton target",
    )
    analyze.add_argument(
        "--proposal",
        required=True,
        type=Path,
        help="recorded JSON model response",
    )
    analyze.add_argument(
        "--model",
        required=True,
        help="model identifier that produced the recorded response",
    )
    analyze.add_argument("--provider", default="recorded")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Edge Catch command-line interface."""
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.command is None:
        parser.print_help()
        return 0

    target_file, separator, qualified_name = arguments.target.rpartition(":")
    if not separator or not target_file or not qualified_name:
        parser.error("--target must use FILE:QUALNAME")

    request = RecordedAnalysisRequest(
        repository=arguments.repository,
        commit=arguments.commit,
        config_path=arguments.config,
        target_file=target_file,
        target_qualified_name=qualified_name,
        proposal_path=arguments.proposal,
        model=arguments.model,
        provider=arguments.provider,
    )
    try:
        report = analyze_recorded(request)
        json_path, markdown_path = write_reports(report, arguments.output)
    except (OSError, ValueError) as error:
        print(f"edge-catch: error: {error}", file=sys.stderr)
        return 2

    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    return 0 if report.status == "completed" else 1
