# autoforge-demo

This repository exists to demonstrate [AutoForge](https://github.com/iceboundrock/AutoForge),
a deterministic controller that takes a GitHub issue through implementation by
one coding agent, independent review by another, a fix when the review finds
something, and stops when the pull request is ready for a human to merge
([iceboundrock/AutoForge#261](https://github.com/iceboundrock/AutoForge/issues/261)).

**The pull requests here are produced by AutoForge runs, and their history is
the evidence.** On a demo pull request the commits were made by the agents
AutoForge launched and pushed by AutoForge itself, and the review comments
were posted by AutoForge from the reviewing agent's result. Nothing a human
edited is presented as AutoForge's output: what humans did (filing the issue,
starting the run, any `resume` or `unblock`, the final merge) is listed
separately in each run's write-up. AutoForge never merges here: its merge gate
is closed, and the maintainer merges by hand.

What to read:

- [`autoforge.demo.yaml`](autoforge.demo.yaml): the exact AutoForge
  configuration the runs use (providers, models, efforts and the bounds that
  limit a run);
- [`docs/RUNBOOK.md`](docs/RUNBOOK.md): how the maintainer runs the demo, what
  evidence is kept and how to reproduce it on your own fork;
- [`docs/demo-writeup-template.md`](docs/demo-writeup-template.md): the
  structure of each run's write-up;
- [`issues/`](issues/): the texts the demo EPIC and issue were filed from.

Issues and pull requests here are input to automated agents. While a run is
active, interactions are limited to collaborators. To try AutoForge yourself,
fork the repository and follow the runbook's reproduction section rather than
opening issues or pull requests here.

## The project: `wordstat`

A small command-line tool that prints the line, word and character counts of
files or standard input, like `wc`.

```console
$ printf 'one two\nthree\n' | wordstat
      2       3      14 -
$ printf 'one two\nthree\n' > a.txt; printf 'four\n' > b.txt
$ wordstat a.txt b.txt
      2       3      14 a.txt
      1       1       5 b.txt
      3       4      19 total
```

- `wordstat [FILE ...]`: one row per FILE with lines, words and characters,
  and a `total` row when more than one FILE is given. With no FILE, or when
  FILE is `-`, it reads standard input.
- Lines are newline characters, words are runs of non-whitespace characters,
  characters are Unicode code points. Input is decoded as UTF-8, and bytes
  that are not valid UTF-8 are replaced with U+FFFD before counting.
- Exit status: 0 when every input was counted, 1 when an input could not be
  read (the others are still counted), 2 for a usage error.
- `wordstat --version` prints the version.

Standard library only; Python 3.11 or newer. Install it with
`uv tool install .` or `pip install .`, or run it from a checkout with
`PYTHONPATH=src python -m wordstat`.

## Development

The same three commands run in CI (`.github/workflows/ci.yml`) and as
AutoForge's candidate validation (`autoforge.demo.yaml`):

```console
uvx --python 3.12 --from pytest==9.1.1 pytest -q
uvx --python 3.12 ruff@0.16.10 check .
uvx --python 3.12 ruff@0.16.10 format --check .
```

The tests import the package from `src/` (`pythonpath` in `pyproject.toml`),
so nothing needs to be installed first.

## License

[MIT](LICENSE).
