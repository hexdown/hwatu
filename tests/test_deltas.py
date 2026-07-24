"""the delta schemas against their own cards, with sample records.

till and flush live in the library (coded, not staked); their genesis
blooms are pinned here as regression fixtures -- recorded at first
sealing, never to drift.
"""

import pytest

from hwatu import deltas, layouts, sips
from hwatu.nodes import Blossom, Face, Stem
from hwatu.schema import load, sips_of
from hwatu.validate import validate_face

TILL_VALUES = deltas.TILL.values()
FLUSH_VALUES = deltas.FLUSH.values()

# pinned at first sealing (2026-07-20): the genesis blooms
TILL_BLOOM = "k?0±!9c3lqr$ef:5rs%π18kψ@·5Σ=ΔqΔnμlΩsh~!xt:g5xwfh1c8·'s3672μΞ6?q"
FLUSH_BLOOM = "μΣu2Γ?j?34mμhλ^jΩ0ju$0πa9!φ&ΩΣdro=~5f#*bf0peeβθuπφ@a2Ξ1Ξ=nwl4μr:"


def neem(word: str) -> Blossom:
    return Blossom(sips.NEEM, layouts.word(word))


def ring(high: int, low: int) -> Blossom:
    return Blossom(TILL_VALUES["ring"], layouts.ring(high, low))


def bloom64() -> Blossom:
    return Blossom(sips.BLOOM, tuple(range(64)))


def record(schema_name: str, act: Stem) -> Face:
    petals = deltas.blooms()[schema_name]
    return Face(0, Stem(sips.SCHEMA, (Blossom(sips.BLOOM, petals), act)), 0)


def test_ring_layout_round_trips():
    assert layouts.ring(1, 0) == (0, 0, 0, 0, 0, 1, 0, 0, 0, 0)
    assert layouts.halves(layouts.ring(1, 0)) == (1, 0)
    top = ((1 << 36) - 1, (1 << 24) - 1)
    assert layouts.halves(layouts.ring(*top)) == top


def test_ring_overflow_is_rejected():
    with pytest.raises(ValueError):
        layouts.ring(1 << 36, 0)
    with pytest.raises(ValueError):
        layouts.ring(0, 1 << 24)
    with pytest.raises(ValueError):
        layouts.halves((0,) * 9)


def test_till_value_table():
    assert TILL_VALUES["found"] == 1
    assert TILL_VALUES["plot"] == 2
    assert TILL_VALUES["stake"] == 3
    assert TILL_VALUES["ring"] == 0o73


def test_flush_value_table():
    assert FLUSH_VALUES["sow"] == 1
    assert FLUSH_VALUES["shoot"] == 2
    assert FLUSH_VALUES["ring"] == TILL_VALUES["ring"]


def test_delta_schemas_round_trip_their_own_cards():
    assert load(sips_of(deltas.TILL)) == deltas.TILL
    assert load(sips_of(deltas.FLUSH)) == deltas.FLUSH


def test_the_genesis_blooms_are_pinned():
    blooms = deltas.blooms()
    assert sips.glyphs(blooms["till"]) == TILL_BLOOM
    assert sips.glyphs(blooms["flush"]) == FLUSH_BLOOM


def test_a_plot_record_validates():
    act = Stem(TILL_VALUES["plot"], (neem("prose"),))
    assert validate_face(record("till", act), deltas.TILL) == ()


def test_a_stake_record_validates():
    act = Stem(TILL_VALUES["stake"], (ring(0, 1), bloom64()))
    assert validate_face(record("till", act), deltas.TILL) == ()


def test_a_sow_record_validates():
    # taproot ring, plot ring, face bloom -- identification first
    act = Stem(FLUSH_VALUES["sow"], (ring(1, 0), ring(0, 2), bloom64()))
    assert validate_face(record("flush", act), deltas.FLUSH) == ()


def test_a_shoot_record_carries_child_rings():
    # card ring, face bloom, then one ring per graft in face order
    act = Stem(
        FLUSH_VALUES["shoot"],
        (ring(1, 3), bloom64(), ring(1, 4), ring(1, 5)),
    )
    assert validate_face(record("flush", act), deltas.FLUSH) == ()


def test_a_sow_read_as_a_till_is_inadmissible():
    # sow and found share a kind value across the two logs; the wrong
    # log's schema rejects the body, child by child
    act = Stem(FLUSH_VALUES["sow"], (ring(1, 0), ring(0, 2), bloom64()))
    verdicts = validate_face(record("till", act), deltas.TILL)
    assert [v.rule for v in verdicts] == ["admission"] * 3
