"""the sip value space: families, glyphs, base-36 petals."""

from hwatu import layouts
from hwatu import sips


def test_glyph_table_is_a_bijection():
    assert len(sips.GLYPHS) == 64
    assert len(set(sips.GLYPHS)) == 64
    for value, glyph in enumerate(sips.GLYPHS):
        assert sips.VALUES[glyph] == value


def test_families_by_leading_bits():
    assert sips.family(0o00) is sips.Family.STEM  # schema node
    assert sips.family(0o37) is sips.Family.STEM
    assert sips.family(0o40) is sips.Family.BOUGH
    assert sips.family(0o57) is sips.Family.BOUGH  # Ω, the first bough
    assert sips.family(0o60) is sips.Family.BLOSSOM
    assert sips.family(0o76) is sips.Family.BLOSSOM  # bloom
    assert sips.family(0o77) is sips.Family.PAD


def test_petals_are_base_36():
    for ch in "0123456789abcdefghijklmnopqrstuvwxyz":
        assert layouts.word(ch) == (int(ch, 36),)


def test_reserved_glyphs():
    assert sips.GLYPHS[sips.NEEM] == "·"  # the interpunct opens every word
    assert sips.GLYPHS[sips.GRAFT] == "'"
    assert sips.GLYPHS[sips.BLOOM] == "*"
    assert sips.GLYPHS[sips.NULL] == "-"
    assert sips.GLYPHS[0o57] == "Ω"  # first conventional bough seat
    assert sips.GLYPHS[0o73] == "^"  # conventional first blossom: prop


def test_words_with_small_marks():
    assert layouts.word("caw-caw") == (12, 10, 32, sips.BEAT, 12, 10, 32)
    assert layouts.word("haven't") == (17, 10, 31, 14, 23, sips.ELIDE, 29)
    assert layouts.word("flop*s") == (15, 21, 24, 25, sips.POSSESS, 28)


def test_word_text_round_trip():
    for w in ("caw-caw", "feather", "haven't", "flop*s", "to-day"):
        assert layouts.text(layouts.word(w)) == w


def test_neem_streams_sort_alphabetically():
    words = ["bet", "billy", "feather", "flop", "mary"]
    assert sorted(words) == sorted(words, key=layouts.word)
