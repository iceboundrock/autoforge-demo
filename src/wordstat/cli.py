"""The ``wordstat`` command line."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from wordstat import __version__
from wordstat.counts import Counts, count_text

STDIN = "-"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wordstat",
        description=(
            "Print the line, word and character counts of each FILE, and a total "
            "line when more than one FILE is given. With no FILE, or when FILE "
            "is -, read standard input."
        ),
    )
    parser.add_argument("files", nargs="*", metavar="FILE", help="file to count (- for stdin)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def read_text(name: str) -> str:
    """The text of file ``name`` (``-`` is standard input), decoded as UTF-8.

    Bytes that are not valid UTF-8 become U+FFFD, so counting never fails on
    an encoding error.
    """
    if name == STDIN:
        data = sys.stdin.buffer.read()
    else:
        with open(name, "rb") as handle:
            data = handle.read()
    return data.decode("utf-8", errors="replace")


def format_row(counts: Counts, name: str) -> str:
    return f"{counts.lines:>7} {counts.words:>7} {counts.chars:>7} {name}"


def main(argv: Sequence[str] | None = None) -> int:
    """Run ``wordstat``; return the exit status.

    0 when every input was counted, 1 when at least one could not be read
    (the others are still counted), 2 for a usage error (from argparse).
    """
    args = build_parser().parse_args(argv)
    names = args.files or [STDIN]
    total = Counts()
    status = 0
    for name in names:
        try:
            text = read_text(name)
        except OSError as exc:
            print(f"wordstat: {name}: {exc.strerror or exc}", file=sys.stderr)
            status = 1
            continue
        counts = count_text(text)
        total += counts
        print(format_row(counts, name))
    if len(names) > 1:
        print(format_row(total, "total"))
    return status
