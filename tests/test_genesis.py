"""the karnak orchard against its schemas: genesis, validated.

eight records and ten faces. every record validates under its log's
schema, the readme parses under the real mary frances arbor, the sow
and shoot tails match their faces' grafts, and the orchard
introduces itself through the renderer.
"""

import genesis
import mary_frances
from genesis import FLUSHES, TILLS

from hwatu import deltas, layouts, nodes, slurp
from hwatu.render import render_face
from hwatu.validate import validate_face


def test_the_orchard_is_named_karnak():
    act = genesis.FOUND.root.kids[1]
    assert isinstance(act, nodes.Stem)
    orchard = act.kids[0]
    assert isinstance(orchard, nodes.Blossom)
    assert layouts.text(orchard.petals) == "karnak"


def test_every_till_validates():
    for _, record in TILLS:
        assert validate_face(record, deltas.TILL) == ()


def test_every_flush_validates():
    for _, record in FLUSHES:
        assert validate_face(record, deltas.FLUSH) == ()


def test_the_orchard_springs_up_in_one_second():
    stamps = [stamp for stamp, _ in (*TILLS, *FLUSHES)]
    assert stamps == [(genesis.FOUNDED, n) for n in range(8)]


def test_the_plots_break_ground_in_order():
    names = []
    for _, record in TILLS[1:5]:
        act = record.root.kids[1]
        names.append(layouts.text(act.kids[0].petals))
    assert names == ["plots", "schemas", "gardeners", "prose"]


def test_the_stake_ties_prose_to_the_taproot_bloom():
    act = genesis.STAKE.root.kids[1]
    lineage, taproot_bloom = act.kids
    assert layouts.halves(lineage.petals) == genesis.PROSE_LINEAGE_RING
    assert taproot_bloom.petals == genesis.MF_BLOOMS["taproot"]


def test_the_readme_taproot_validates_under_the_real_arbor():
    verdicts = validate_face(genesis.README_TAPROOT_FACE, mary_frances.TAPROOT)
    assert verdicts == ()
    bough = genesis.README_TAPROOT_FACE.root.kids[1]
    assert bough.kids[0].petals == (mary_frances.TAPROOT.values()["passage"],)


def test_the_readme_passage_validates():
    verdicts = validate_face(genesis.README_PASSAGE_FACE, mary_frances.PASSAGE)
    assert verdicts == ()


def test_the_orchard_introduces_itself():
    text = render_face(genesis.README_PASSAGE_FACE, mary_frances.PASSAGE)
    assert text == genesis.README_TEXT


def test_the_sow_tail_matches_the_taproot_grafts():
    act = genesis.SOW.root.kids[1]
    taproot_ring, plot_ring, _, child = act.kids
    assert layouts.halves(taproot_ring.petals) == genesis.TAPROOT_RING
    assert layouts.halves(plot_ring.petals) == genesis.PROSE_RING
    assert layouts.halves(child.petals) == genesis.README_RING
    bough = genesis.README_TAPROOT_FACE.root.kids[1]
    assert len(act.kids) - 3 == len(bough.kids)  # one ring per graft


def test_the_shoot_supplies_the_forward_referenced_leaf():
    act = genesis.SHOOT.root.kids[1]
    card_ring, face_bloom = act.kids  # a leaf carries no child rings
    assert layouts.halves(card_ring.petals) == genesis.README_RING
    assert face_bloom.petals == genesis.sealed_bloom(
        genesis.README_PASSAGE_FACE
    )


def test_the_constellation_counts():
    seeded = genesis.faces()
    assert len(seeded) == 10
    assert len(TILLS) + len(FLUSHES) == 8
    blooms = {slurp.bloom_of(data) for data in seeded.values()}
    assert len(blooms) == 10  # every face distinct
