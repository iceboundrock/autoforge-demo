import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

import wordstat
from wordstat.cli import main


@pytest.fixture
def stdin(monkeypatch):
    def feed(data: bytes) -> None:
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))

    return feed


def test_reads_stdin_without_arguments(stdin, capsys):
    stdin(b"one two\nthree\n")
    assert main([]) == 0
    assert capsys.readouterr().out == "      2       3      14 -\n"


def test_dash_is_stdin(stdin, capsys):
    stdin(b"x\n")
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "      1       1       2 -\n"


def test_one_file_has_no_total(tmp_path, capsys):
    path = tmp_path / "a.txt"
    path.write_text("hello world\n", encoding="utf-8")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == f"      1       2      12 {path}\n"


def test_several_files_end_with_a_total(tmp_path, capsys):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("one\n", encoding="utf-8")
    b.write_text("two three\nfour\n", encoding="utf-8")
    assert main([str(a), str(b)]) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"      1       1       4 {a}",
        f"      2       3      15 {b}",
        "      3       4      19 total",
    ]


def test_unreadable_file_is_reported_and_the_rest_counted(tmp_path, capsys):
    good = tmp_path / "good.txt"
    good.write_text("a b\n", encoding="utf-8")
    missing = tmp_path / "missing.txt"
    assert main([str(missing), str(good)]) == 1
    captured = capsys.readouterr()
    assert captured.out == f"      1       2       4 {good}\n      1       2       4 total\n"
    assert captured.err == f"wordstat: {missing}: No such file or directory\n"


def test_invalid_utf8_is_replaced_not_fatal(stdin, capsys):
    stdin(b"caf\xe9 ok\n")
    assert main([]) == 0
    assert capsys.readouterr().out == "      1       2       8 -\n"


def test_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out == f"wordstat {wordstat.__version__}\n"


def test_runs_as_a_module():
    src = Path(wordstat.__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "wordstat"],
        input=b"a b c\n",
        capture_output=True,
        env={**os.environ, "PYTHONPATH": str(src)},
        check=True,
    )
    assert result.stdout == b"      1       3       6 -\n"
