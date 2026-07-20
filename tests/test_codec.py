"""the codec against the golden card (spec/design/card3-golden.md).

the hand is the test for the machine: card 3 of chapter 4, hand-spelled
to 141 exact sips, must round-trip byte-for-byte.
"""

import pytest

from hwatu import layouts
from hwatu import sips as s
from hwatu.codec import Truncated, encode, encode_face, parse, parse_face
from hwatu.nodes import Blossom, Face, Pad, Stem

# passage-schema kind values (spec/design/passage-schema.md) -- test
# constants, deliberately not part of hwatu: content kinds are data.
PARAGRAPH, STATEMENT, EXCLAMATION, TURN, PHRASE = 1, 2, 4, 6, 9
PROP = 0o73  # conventional first blossom


def neem(w: str) -> Blossom:
    return Blossom(s.NEEM, layouts.word(w))


def prop(w: str) -> Blossom:
    return Blossom(PROP, layouts.word(w))


def phrase(*words: Blossom) -> Stem:
    return Stem(PHRASE, words)


CAW_CAW = Stem(TURN, (Stem(EXCLAMATION, (phrase(neem("caw-caw")),)),))

CARD_3_BODY = Stem(
    PARAGRAPH,
    (
        CAW_CAW,
        Stem(
            STATEMENT,
            (
                phrase(
                    prop("feather"),
                    prop("flop"),
                    neem("cleared"),
                    neem("his"),
                    neem("throat"),
                ),
            ),
        ),
        CAW_CAW,
    ),
)

# the golden body values, transcribed from card3-golden.md
GOLDEN_BODY = (
    # paragraph, 3 children
    *(1, 2),
    # turn > exclamation > phrase > neem caw-caw
    *(6, 0, 4, 0, 9, 0),
    *(60, 6, 12, 10, 32, 63, 12, 10, 32),
    # statement > phrase(5)
    *(2, 0, 9, 4),
    *(59, 6, 15, 14, 10, 29, 17, 14, 27),  # ^feather
    *(59, 3, 15, 21, 24, 25),  # ^flop
    *(60, 6, 12, 21, 14, 10, 27, 14, 13),  # ·cleared
    *(60, 2, 17, 18, 28),  # ·his
    *(60, 5, 29, 17, 27, 24, 10, 29),  # ·throat
    # turn > exclamation > phrase > neem caw-caw
    *(6, 0, 4, 0, 9, 0),
    *(60, 6, 12, 10, 32, 63, 12, 10, 32),
)

GOLDEN_BODY_GLYPHS = (
    "12604090·6caw-caw2094^6feather^3flop·6cleared·2his·5throat604090·6caw-caw"
)


def test_golden_body_values():
    assert encode(CARD_3_BODY) == GOLDEN_BODY


def test_golden_body_glyphs():
    assert s.glyphs(encode(CARD_3_BODY)) == GOLDEN_BODY_GLYPHS


def test_golden_body_round_trip():
    node, at = parse(GOLDEN_BODY)
    assert node == CARD_3_BODY
    assert at == len(GOLDEN_BODY)


def test_golden_face_is_141_sips():
    # schema bloom held by a placeholder until the passage schema card
    # is encoded and hashed; the null hash stands in (64 beats).
    bloom = Blossom(s.BLOOM, (s.BEAT,) * 64)
    face = Face(0, Stem(s.SCHEMA, (bloom, CARD_3_BODY)), 0)
    stream = encode_face(face)
    assert len(stream) == 141
    assert s.glyphs(stream[:4]) == "01*-"  # the card-opener signature
    assert parse_face(stream) == face


def test_face_pads_are_identity():
    bloom = Blossom(s.BLOOM, (s.BEAT,) * 64)
    face = Face(3, Stem(s.SCHEMA, (bloom, CAW_CAW)), 5)
    stream = encode_face(face)
    assert stream[:3] == (s.NULL,) * 3
    assert stream[-5:] == (s.NULL,) * 5
    assert parse_face(stream) == face


def test_pad_in_child_position_round_trips():
    # a pad in a declaration slot skips a seat (spec/encoding.md)
    node = Stem(1, (Pad(), neem("held")))
    assert parse(encode(node))[0] == node


def test_truncation_says_what_is_missing():
    stream = encode(CARD_3_BODY)[:-3]
    with pytest.raises(Truncated):
        parse(stream)


def test_counts_are_1_to_64():
    with pytest.raises(ValueError):
        encode(Stem(1, ()))
    with pytest.raises(ValueError):
        encode(Blossom(s.BLOOM, (s.BEAT,) * 65))
