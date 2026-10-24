from wordstat.counts import Counts, count_text


def test_empty_text_counts_nothing():
    assert count_text("") == Counts(0, 0, 0)


def test_lines_words_and_characters():
    assert count_text("one two\nthree\n") == Counts(lines=2, words=3, chars=14)


def test_last_line_without_newline_is_not_a_line():
    assert count_text("a\nb") == Counts(lines=1, words=2, chars=3)


def test_any_whitespace_separates_words():
    assert count_text("  a\tb  c\n\n").words == 3


def test_characters_are_code_points_not_bytes():
    assert count_text("héllo wörld\n").chars == 12


def test_counts_add_up():
    assert Counts(1, 2, 3) + Counts(10, 20, 30) == Counts(11, 22, 33)
