"""the validator against the golden card and its mutations.

parse always returns a tree; validate returns the verdicts. card 3 is
innocent under the passage schema, and a mutated stream earns exactly
its own verdicts, located by path, the rest of the tree unimpeached.
"""

from mary_frances import PASSAGE, SECTION
from test_codec import CARD_3_BODY

from hwatu import layouts, sips
from hwatu.codec import encode_face, parse_face
from hwatu.nodes import Blossom, Bough, Face, Pad, Stem
from hwatu.validate import validate, validate_face

VALUES = PASSAGE.values()
SECTION_VALUES = SECTION.values()

NULL_BLOOM = Blossom(sips.BLOOM, (sips.BEAT,) * 64)
GOLDEN_FACE = Face(0, Stem(sips.SCHEMA, (NULL_BLOOM, CARD_3_BODY)), 0)

# landmarks in the golden face stream: 68 sips of schema node + bloom,
# then the body -- the first neem's kind sip and the statement's
STREAM = encode_face(GOLDEN_FACE)
NEEM_AT = 76
STATEMENT_AT = 85


def mutated(at: int, to: int) -> Face:
    return parse_face((*STREAM[:at], to, *STREAM[at + 1 :]))


def graft(name: str) -> Blossom:
    return Blossom(sips.GRAFT, (SECTION_VALUES[name],))


def test_card_3_validates_under_the_passage_schema():
    assert validate_face(GOLDEN_FACE, PASSAGE) == ()


def test_a_bare_subtree_validates_too():
    assert validate(CARD_3_BODY, PASSAGE) == ()


def test_a_mutated_kind_is_one_verdict_not_a_global_failure():
    assert STREAM[STATEMENT_AT] == VALUES["statement"]
    verdicts = validate_face(mutated(STATEMENT_AT, 0o37), PASSAGE)
    assert [v.rule for v in verdicts] == ["admission"]
    assert verdicts[0].path == (1, 1)


def test_the_verdict_path_reaches_a_mutated_leaf():
    assert STREAM[NEEM_AT] == sips.NEEM
    verdicts = validate_face(mutated(NEEM_AT, 0o72), PASSAGE)
    assert [v.rule for v in verdicts] == ["admission"]
    assert verdicts[0].path == (1, 0, 0, 0, 0)


def test_two_mutations_earn_two_verdicts():
    twice = list(STREAM)
    twice[NEEM_AT] = 0o72
    twice[STATEMENT_AT] = 0o37
    verdicts = validate_face(parse_face(tuple(twice)), PASSAGE)
    assert {v.path for v in verdicts} == {(1, 0, 0, 0, 0), (1, 1)}


def test_a_sentence_cannot_wear_the_crown():
    turn = CARD_3_BODY.kids[0]  # a legal tree under an uncrowned root
    face = Face(0, Stem(sips.SCHEMA, (NULL_BLOOM, turn)), 0)
    verdicts = validate_face(face, PASSAGE)
    assert [v.rule for v in verdicts] == ["crown"]
    assert verdicts[0].path == (1,)


def test_a_pad_child_is_an_intentional_absence():
    held = Blossom(sips.NEEM, layouts.word("held"))
    phrase = Stem(VALUES["phrase"], (Pad(), held))
    assert validate(phrase, PASSAGE) == ()


def test_a_branch_face_validates_under_the_section_schema():
    bough = Bough(
        SECTION_VALUES["section"], (graft("banner"), graft("passage"))
    )
    face = Face(0, Stem(sips.SCHEMA, (NULL_BLOOM, bough)), 0)
    assert validate_face(face, SECTION) == ()


def test_bough_children_are_all_grafts():
    stray = Blossom(sips.NEEM, layouts.word("weed"))
    bough = Bough(SECTION_VALUES["section"], (graft("banner"), stray))
    verdicts = validate(bough, SECTION)
    assert [v.rule for v in verdicts] == ["family"]
    assert verdicts[0].path == (1,)


def test_a_pad_under_a_bough_is_reported():
    # the strict reading of "children must all be grafts"; whether a
    # pad may hold an absent graft slot is an open spec question
    bough = Bough(SECTION_VALUES["section"], (Pad(),))
    assert [v.rule for v in validate(bough, SECTION)] == ["family"]


def test_a_graft_petal_names_a_grafted_position_kind():
    stray = Blossom(sips.GRAFT, (0o01,))
    bough = Bough(SECTION_VALUES["section"], (stray,))
    assert [v.rule for v in validate(bough, SECTION)] == ["graft"]


def test_a_graft_carries_exactly_one_petal():
    fat = Blossom(
        sips.GRAFT, (SECTION_VALUES["banner"], SECTION_VALUES["passage"])
    )
    bough = Bough(SECTION_VALUES["section"], (fat,))
    assert [v.rule for v in validate(bough, SECTION)] == ["arity"]


def test_a_face_needs_its_bloom():
    face = Face(0, Stem(sips.SCHEMA, (Pad(), CARD_3_BODY)), 0)
    verdicts = validate_face(face, PASSAGE)
    assert [v.rule for v in verdicts] == ["face"]
    assert verdicts[0].path == (0,)


def test_a_schema_node_holds_bloom_and_card_root():
    face = Face(0, Stem(sips.SCHEMA, (NULL_BLOOM,)), 0)
    assert [v.rule for v in validate_face(face, PASSAGE)] == ["face"]
