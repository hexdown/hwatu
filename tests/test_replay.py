"""the karnak orchard, opened: replay distills the projections.

from nothing but the log and the seeded faces: the name, the plot
table, the schema registry, the documents, the backs, and the
allocator -- then the walk from taproot ring to rendered welcome,
with the readme's schema resolved from the seeded faces by bloom.
"""

import genesis
import pytest
from genesis import FLUSHES, TILLS

from hwatu import nodes, orchard, slurp
from hwatu.codec import parse_face
from hwatu.render import render_face
from hwatu.schema import load

KARNAK = orchard.replay(TILLS, FLUSHES, genesis.faces().values())


def test_the_orchard_is_karnak_with_four_plots():
    assert KARNAK.name == "karnak"
    assert KARNAK.plots == {
        (0, 1): "plots",
        (0, 2): "schemas",
        (0, 3): "gardeners",
        (0, 4): "prose",
    }


def test_the_prose_lineage_is_staked():
    assert KARNAK.registry == {(0, 5): genesis.MF_BLOOMS["taproot"]}


def test_the_readme_document_is_sown_in_prose():
    assert KARNAK.documents == {(0, 0): (0, 4)}
    taproot = KARNAK.backs[(0, 0)]
    assert taproot.bloom == genesis.sealed_bloom(genesis.README_TAPROOT_FACE)
    assert taproot.kids == ((0, 6),)
    leaf = KARNAK.backs[(0, 6)]
    assert leaf.bloom == genesis.sealed_bloom(genesis.README_PASSAGE_FACE)
    assert leaf.kids == ()


def test_the_allocator_resumes_where_genesis_left_off():
    assert KARNAK.next_document == 1
    assert KARNAK.next_step[0] == 7


def test_unknown_acts_skip_gracefully():
    mystery = genesis.face(
        genesis.DELTA_BLOOMS["till"],
        nodes.Stem(0o20, (genesis.neem("mystery"),)),
    )
    tills = (*TILLS, ((genesis.FOUNDED, 8), mystery))
    opened = orchard.replay(tills, FLUSHES, genesis.faces().values())
    assert opened.name == "karnak"
    assert opened.plots == KARNAK.plots


def test_a_later_shoot_replaces_the_face():
    fresh = tuple(range(64))
    reshoot = genesis.face(
        genesis.DELTA_BLOOMS["flush"],
        nodes.Stem(
            genesis.FLUSH_VALUES["shoot"],
            (genesis.ring(0, 6), genesis.bloom(fresh)),
        ),
    )
    flushes = (*FLUSHES, ((genesis.FOUNDED, 8), reshoot))
    opened = orchard.replay(TILLS, flushes, genesis.faces().values())
    assert opened.backs[(0, 6)].bloom == fresh


def test_the_ring_tail_is_checked_against_the_face():
    # the passage face holds no grafts; a child ring is a lie
    readme_bloom = genesis.sealed_bloom(genesis.README_PASSAGE_FACE)
    lying = genesis.face(
        genesis.DELTA_BLOOMS["flush"],
        nodes.Stem(
            genesis.FLUSH_VALUES["shoot"],
            (
                genesis.ring(0, 6),
                genesis.bloom(readme_bloom),
                genesis.ring(0, 7),
            ),
        ),
    )
    flushes = (*FLUSHES, ((genesis.FOUNDED, 8), lying))
    with pytest.raises(ValueError):
        orchard.replay(TILLS, flushes, genesis.faces().values())


def test_the_orchard_opens_and_speaks():
    # the full walk: backs -> child ring -> bloom -> face -> schema
    # resolved from the seeded faces by bloom -> the welcome
    seeded = {slurp.bloom_of(data): data for data in genesis.faces().values()}
    taproot = KARNAK.backs[(0, 0)]
    leaf = KARNAK.backs[taproot.kids[0]]
    leaf_face = parse_face(slurp.unpack(seeded[leaf.bloom]))
    governor = leaf_face.root.kids[0]
    assert isinstance(governor, nodes.Blossom)
    speaks = load(slurp.unpack(seeded[governor.petals]))
    assert speaks.name == "passage"
    assert render_face(leaf_face, speaks) == genesis.README_TEXT
