"""the seed chain: six schemas, hash-linked, and the complete pipeline.

the capstone: canonical bytes off the (future) disk, unpacked, parsed
with no schema in hand, interpreted under the passage schema, and
rendered back to the printed page.
"""

import mary_frances
from test_codec import CARD_3_BODY

from hwatu import sips, slurp
from hwatu.codec import encode_face, parse_face
from hwatu.nodes import Blossom, Face, Stem
from hwatu.render import render


def test_the_chain_resolves_in_dependency_order():
    blooms = mary_frances.blooms()
    assert list(blooms) == [
        "passage",
        "banner",
        "section",
        "chapter",
        "book",
        "taproot",
    ]
    assert all(len(bloom) == 64 for bloom in blooms.values())
    assert len(set(blooms.values())) == 6  # six distinct identities


def test_seed_cards_fit_single_slurps():
    for name, data in mary_frances.sealed().items():
        assert len(data) <= 1440, name  # every schema is one card


PASSAGE_BLOOM_GLYPHS = (
    "s-sβi=Ω=3v&9-7vb6ys3!fψfp8&λ*-mψzu0ψ=-b4Σ4pΞ6xk=&%θxΩbt3λ*@^aβφl"
)


def test_the_first_bloom_blooms():
    # the passage schema's real hash: the petals that replaced
    # the golden card's placeholder on 2026-07-20
    passage_bloom = mary_frances.blooms()["passage"]
    assert sips.glyphs(passage_bloom) == PASSAGE_BLOOM_GLYPHS


def test_the_complete_pipeline_bytes_to_speech():
    passage_bloom = mary_frances.blooms()["passage"]
    face = Face(
        0,
        Stem(
            sips.SCHEMA,
            (Blossom(sips.BLOOM, passage_bloom), CARD_3_BODY),
        ),
        0,
    )
    stream = encode_face(face)
    assert len(stream) == 141  # the golden count, now fully real
    data = slurp.pack(slurp.fit(stream))
    assert len(data) == 120  # canonical bytes

    # and back: bytes -> sips -> tree -> speech
    recovered = slurp.unpack(data)
    parsed = parse_face(recovered)
    assert parsed.root.kids[0] == Blossom(sips.BLOOM, passage_bloom)
    assert render(parsed.root.kids[1], mary_frances.PASSAGE) == (
        "“Caw-caw!” Feather Flop cleared his throat. “Caw-caw!”"
    )
