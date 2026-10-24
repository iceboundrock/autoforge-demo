Part of #{{EPIC_NUMBER}}.

## Problem

`wordstat` says how many words a text has, but not which ones. To see the most frequent words today you need a pipeline such as `tr -s '[:space:]' '\n' | sort | uniq -c | sort -rn | head`, which splits words differently from `wordstat` and breaks on non-ASCII text.

## Proposal

Add an option `--top N` that lists the N most frequent words of all inputs, after the usual count rows.

## Specification

1. **The option.** `--top N`, where N is an integer of at least 1. Without `--top`, the output, the exit status and the error messages are byte-for-byte what they are today.
2. **What counts as a word.** Every whitespace-separated token (`str.split()`) of every input that was read successfully, files and standard input alike. Each token is normalized in two steps:
   1. leading and trailing characters for which `str.isalnum()` is false are removed, so `"Hello,"` and `(hello)` both become `hello` after step 2; characters inside the token stay (`don't`, `well-known` and `3.14` are one word each);
   2. its case is folded with `str.casefold()`, which is full Unicode case folding and differs from `str.lower()`: `Straße`, `STRASSE` and `strasse` are the same word, printed as `strasse`.

   A token with no alphanumeric character at all (`--`, `...`, `—`) is not a word for `--top`. The word column is unchanged and keeps counting every token.
3. **Order.** By count, highest first. Words with the same count are ordered by the normalized word in ascending order (plain `str` comparison), never by where they first appear, so the list does not depend on the order of the words in the input or of the files on the command line.
4. **Output.** After every count row (and the `total` row, when there is one), one empty line, then one line per word: the count right-aligned in seven columns, a space, the word, that is `f"{count:>7} {word}"`. At most N lines; fewer when there are fewer distinct words. When the inputs contain no word at all, nothing is added, not even the empty line.
5. **Errors.** `--top 0`, a negative N and a value that is not an integer are usage errors: exit status 2, argparse's usage message on standard error, nothing on standard output. A file that cannot be read is reported as today (exit status 1) and contributes no word; the other inputs are still counted and listed.

## Example

```console
$ printf 'The cat saw the dog.\nA dog, THE end... Straße STRASSE\n' | wordstat --top 3
      2      11      54 -

      3 the
      2 dog
      2 strasse
```

## Tests to add

In a new `tests/test_top.py`, at least one test for each of these:

- the example above, byte for byte;
- `The the THE` counts as one word, `the`, three times;
- `Straße STRASSE strasse` counts as one word, `strasse`, three times;
- leading and trailing punctuation is removed and inner punctuation kept: `"Hello," (hello) hello!` is `hello` three times; `don't don't well-known` is `don't` twice and `well-known` once;
- tokens without an alphanumeric character are not listed but still count in the word column: input `-- ... —` prints a word count of 3 and no top list (no empty line);
- ties: input `b a b a c` lists `a`, `b`, `c` in that order (`      2 a`, `      2 b`, `      1 c`);
- the list is the same when the same files are given in the opposite order;
- words are counted across several files and standard input (`-`) together;
- N limits the list, and an N larger than the number of distinct words lists every word;
- `--top 0`, `--top -1` and `--top x` exit with status 2, print a usage error on standard error and nothing on standard output;
- with an unreadable file among the inputs, the exit status is 1 and the words of the other inputs are listed;
- without `--top`, the output is unchanged (the existing tests keep passing unchanged).

## Constraints

- Python standard library only, no new dependency; keep Python 3.11 compatibility (`requires-python = ">=3.11"`).
- Document `--top` in `README.md`, in the usage section.
- Do not change `.github/workflows/`, `autoforge.demo.yaml`, `LICENSE`, `docs/` or `issues/`.
- Before you finish, these pass in the repository root (the same commands CI runs):

  ```console
  uvx --python 3.12 --from pytest==9.1.1 pytest -q
  uvx --python 3.12 ruff@0.16.10 check .
  uvx --python 3.12 ruff@0.16.10 format --check .
  ```

## Done when

- [ ] `wordstat --top N` behaves as specified above, the example included.
- [ ] `tests/test_top.py` covers every item of "Tests to add".
- [ ] `README.md` documents `--top`.
- [ ] Output without `--top` is unchanged and the existing tests pass unchanged.
- [ ] The three commands above pass.
