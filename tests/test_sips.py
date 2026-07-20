"""the sip value space: families, glyphs, base-36 petals."""

from hwatu import layouts
from hwatu import sips as s


def test_glyph_table_is_a_bijection():
    assert len(s.GLYPHS) == 64
    assert len(set(s.GLYPHS)) == 64
    for value, glyph in enumerate(s.GLYPHS):
        assert s.VALUES[glyph] == value


def test_families_by_leading_bits():
    assert s.family(0o00) is s.Family.STEM  # schema node
    assert s.family(0o37) is s.Family.STEM
    assert s.family(0o40) is s.Family.BOUGH
    assert s.family(0o57) is s.Family.BOUGH  # Ω, the first bough
    assert s.family(0o60) is s.Family.BLOSSOM
    assert s.family(0o76) is s.Family.BLOSSOM  # bloom
    assert s.family(0o77) is s.Family.PAD


def test_petals_are_base_36():
    for ch in "0123456789abcdefghijklmnopqrstuvwxyz":
        assert layouts.word(ch) == (int(ch, 36),)


def test_reserved_glyphs():
    assert s.GLYPHS[s.NEEM] == "·"  # the interpunct opens every word
    assert s.GLYPHS[s.GRAFT] == "'"
    assert s.GLYPHS[s.BLOOM] == "*"
    assert s.GLYPHS[s.NULL] == "-"
    assert s.GLYPHS[0o57] == "Ω"  # first conventional bough seat
    assert s.GLYPHS[0o73] == "^"  # conventional first blossom: prop


def test_words_with_small_marks():
    assert layouts.word("caw-caw") == (12, 10, 32, s.BEAT, 12, 10, 32)
    assert layouts.word("haven't") == (17, 10, 31, 14, 23, s.ELIDE, 29)
    assert layouts.word("flop*s") == (15, 21, 24, 25, s.POSSESS, 28)


def test_word_text_round_trip():
    for w in ("caw-caw", "feather", "haven't", "flop*s", "to-day"):
        assert layouts.text(layouts.word(w)) == w


def test_neem_streams_sort_alphabetically():
    words = ["bet", "billy", "feather", "flop", "mary"]
    assert sorted(words) == sorted(words, key=layouts.word)
