"""schemas as data: the passage schema, machine-encoded at last.

builds the passage schema per spec/design/passage-schema.md, checks
its value table, and round-trips it through its own card face -- the
first schema card hexdown has ever produced by machine.
"""

import pytest

from hwatu import layouts
from hwatu import sips
from hwatu.schema import (
    Grafts,
    Kids,
    Kind,
    Layout,
    Ref,
    Schema,
    Skip,
    load,
    sips_of,
)

from mary_frances import PASSAGE, SECTION


def test_passage_value_table():
    # spec/design/passage-schema.md: stems ascend, blossoms descend
    v = PASSAGE.values()
    assert v["paragraph"] == 1
    assert v["statement"] == 2
    assert v["question"] == 3
    assert v["exclamation"] == 4
    assert v["broken"] == 5
    assert v["turn"] == 6
    assert v["quoth"] == 7
    assert v["fade"] == 8
    assert v["phrase"] == 9
    assert v["pivot"] == 10
    assert v["prop"] == 0o73  # conventional first blossom: ^
    assert v["neem"] == sips.NEEM  # reserved kinds are always nameable


def test_passage_card_opens_like_a_schema_card():
    stream = sips_of(PASSAGE)
    assert sips.glyphs(stream[:4]) == "01*-"
    assert stream[4:68] == (sips.BEAT,) * 64  # the null hash


def test_passage_round_trips_through_its_own_card():
    assert load(sips_of(PASSAGE)) == PASSAGE


def test_quoth_admitted_at_two_levels():
    # the level is the meaning, encoded as membership in two kids lists
    v = PASSAGE.values()
    turn = PASSAGE.kind("turn").spec
    assert isinstance(turn, Kids)
    assert "quoth" in turn.names

    statement = PASSAGE.kind("statement").spec
    assert isinstance(statement, Kids)
    assert "quoth" in statement.names

    assert v["quoth"] == 7


# the real section schema, exercised with placeholder hashes
HASH_A = tuple(range(64))
HASH_B = tuple(reversed(range(64)))


def test_bough_is_derived_and_wears_omega():
    v = SECTION.values()
    assert v["banner"] == 0o73  # position kinds take blossom seats
    assert v["passage"] == 0o72
    assert v["section"] == 0o57  # the bough descends from Ω
    assert sips.GLYPHS[v["section"]] == "Ω"


def test_bough_schema_round_trips_structurally():
    refs = {"banner": HASH_A, "passage": HASH_B}
    parsed = load(sips_of(SECTION, refs))
    assert parsed.name == "section"
    assert parsed.crowns == ("section",)
    # authored refs name their targets; parsed refs carry the petals
    assert parsed.kinds[0] == Kind("banner", Ref(petals=HASH_A))
    assert parsed.kinds[1] == Kind("passage", Ref(petals=HASH_B))
    assert parsed.kinds[2] == Kind("section", Grafts(("banner", "passage")))


def test_a_stem_admitting_position_kinds_is_an_error():
    bad = Schema(
        name="bad",
        crowns=("mixed",),
        kinds=(
            Kind("pos", Ref("elsewhere")),
            Kind("mixed", Kids(("pos", "neem"))),
        ),
    )
    with pytest.raises(ValueError):
        bad.values()


def test_a_bough_grafting_content_kinds_is_an_error():
    bad = Schema(
        name="bad",
        crowns=("bough",),
        kinds=(
            Kind("pos", Ref("elsewhere")),
            Kind("word", Kids(("neem",))),
            Kind("bough", Grafts(("pos", "word"))),
        ),
    )
    with pytest.raises(ValueError):
        bad.values()


def test_skips_hold_seats_by_lookahead():
    pinned = Schema(
        name="pinned",
        crowns=("a",),
        kinds=(
            Skip(),  # skips a stem seat: the next kind is a stem
            Kind("a", Kids(("neem",))),
            Skip(),  # skips a blossom seat: the next kind is a blossom
            Kind("p", Layout(layouts.PHONEME)),
        ),
    )
    v = pinned.values()
    assert v["a"] == 0o02  # 0o01 skipped
    assert v["p"] == 0o72  # 0o73 skipped
    assert load(sips_of(pinned)) == pinned  # pads survive the face
