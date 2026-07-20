"""slurps: packing, sizing, blooms, and collision redistribution."""

import pytest

from hwatu import sips, slurp


def test_pack_unpack_round_trip():
    values = tuple(range(64)) * 2  # 128 sips, increment-aligned
    assert slurp.unpack(slurp.pack(values)) == values


def test_fit_sizes_to_increments():
    assert len(slurp.fit(())) == 32  # minimum one increment
    assert len(slurp.fit((1,) * 32)) == 32  # exact fit, no slack
    assert len(slurp.fit((1,) * 33)) == 64


def test_the_golden_card_slurp_arithmetic():
    # card3-golden.md: 141 content sips -> 160-sip / 120-byte slurp
    content = (1,) * 141
    sized = slurp.fit(content)
    assert len(sized) == 160
    assert sized[141:] == (sips.NULL,) * 19
    assert len(slurp.pack(sized)) == 120


def test_blooms_are_64_petals_and_deterministic():
    data = slurp.seal((1, 2, 3))
    bloom = slurp.bloom_of(data)
    assert len(bloom) == 64
    assert all(0 <= petal <= 63 for petal in bloom)
    assert bloom == slurp.bloom_of(data)
    assert bloom != slurp.bloom_of(slurp.seal((3, 2, 1)))


def test_redistribution_shifts_then_grows():
    first = slurp.fit((1,) * 30)  # 32 sips: no lead, 2 slack
    second = slurp.redistribute(first)
    assert len(second) == 32
    assert second[0] == sips.NULL and second[1] != sips.NULL
    third = slurp.redistribute(slurp.redistribute(second))
    assert len(third) == 64  # slack spent: grew an increment
    # the content survives every shift
    content = tuple(v for v in third if v != sips.NULL)
    assert content == (1,) * 30


def test_redistribution_changes_the_bloom():
    first = slurp.fit((1,) * 30)
    second = slurp.redistribute(first)
    assert slurp.bloom_of(slurp.pack(first)) != slurp.bloom_of(
        slurp.pack(second)
    )


def test_oversized_content_is_rejected():
    with pytest.raises(ValueError):
        slurp.fit((1,) * (slurp.MAX_SIPS + 1))
