"""Counting lines, words and characters of a text."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Counts:
    """Line, word and character counts."""

    lines: int = 0
    words: int = 0
    chars: int = 0

    def __add__(self, other: Counts) -> Counts:
        return Counts(
            lines=self.lines + other.lines,
            words=self.words + other.words,
            chars=self.chars + other.chars,
        )


def count_text(text: str) -> Counts:
    """Count ``text`` the way ``wc`` does.

    Lines are newline characters, so a last line without one is not counted.
    Words are runs of non-whitespace characters (``str.split()``).
    Characters are Unicode code points.
    """
    return Counts(lines=text.count("\n"), words=len(text.split()), chars=len(text))
