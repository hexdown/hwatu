"""chapter 4, card by card: each card seals, validates, and renders
its own printed lines (normalized per the decided rules).

the hand is the test for the machine, one paragraph at a time: the
constructors follow the annotation, the expected strings follow the
corpus, and card 3 must reproduce the golden body exactly.
"""

import mary_frances
import pytest
import test_codec
from data import chapter_4

from hwatu import slurp, validate
from hwatu.codec import encode, encode_face
from hwatu.render import render_face


@pytest.mark.parametrize("number", sorted(chapter_4.CARDS))
def test_every_card_seals_and_validates(number: int):
    face = chapter_4.CARDS[number]()
    sealed = slurp.seal(encode_face(face))
    assert len(sealed) <= 1440
    assert validate.validate_face(face, mary_frances.PASSAGE) == ()


@pytest.mark.parametrize("number", sorted(chapter_4.RENDERED))
def test_cards_render_their_printed_lines(number: int):
    face = chapter_4.CARDS[number]()
    rendered = render_face(face, mary_frances.PASSAGE)
    assert rendered == chapter_4.RENDERED[number]


def test_card_3_matches_the_golden_body():
    body = chapter_4.card_3().root.kids[1]
    assert encode(body) == test_codec.GOLDEN_BODY


def test_the_banner_seals_and_validates():
    face = chapter_4.banner()
    assert len(slurp.seal(encode_face(face))) <= 1440
    assert validate.validate_face(face, mary_frances.BANNER) == ()


def test_the_banner_renders_the_chapter_heading():
    rendered = render_face(chapter_4.banner(), mary_frances.BANNER)
    assert rendered == chapter_4.BANNER_RENDERED


def test_the_branch_cards_seal_and_validate():
    section = chapter_4.section_card()
    assert validate.validate_face(section, mary_frances.SECTION) == ()
    taproot = chapter_4.taproot_card()
    assert validate.validate_face(taproot, mary_frances.TAPROOT) == ()
