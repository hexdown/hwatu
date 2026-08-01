"""the karnak orchard: the hand-coded mary frances genesis. fixtures.

eight records spring the orchard up in its founding second -- found,
four plots broken, the prose lineage staked to the mary frances
taproot, and the readme document sown: a taproot card grafting one
passage leaf, both parsed under the real mary frances arbor. the
whole orchard reconstructs from these records plus ten seeded faces.
per spec/design/genesis.md and spec/design/delta-schemas.md.
"""

import mary_frances

from hwatu import deltas, layouts, sips, slurp, store
from hwatu.codec import encode_face
from hwatu.nodes import Blossom, Bough, Face, Stem
from hwatu.store import Store

# the founding second: the moment the karnak orchard was hand-coded
# into being (2026-07-24 06:30:37 utc)
FOUNDED = 1784874637

# document 0's rings: (0, 0) is the taproot by rule; the rest mint
# in log order
TAPROOT_RING = (0, 0)
PLOTS_RING = (0, 1)
SCHEMAS_RING = (0, 2)
GARDENERS_RING = (0, 3)
PROSE_RING = (0, 4)
PROSE_LINEAGE_RING = (0, 5)
README_RING = (0, 6)

TILL_VALUES = deltas.TILL.values()
FLUSH_VALUES = deltas.FLUSH.values()
PASSAGE_VALUES = mary_frances.PASSAGE.values()
TAPROOT_VALUES = mary_frances.TAPROOT.values()

DELTA_BLOOMS = deltas.blooms()
MF_BLOOMS = mary_frances.blooms()


def neem(word: str) -> Blossom:
    return Blossom(sips.NEEM, layouts.word(word))


def prop(word: str) -> Blossom:
    return Blossom(PASSAGE_VALUES["prop"], layouts.word(word))


def ring(high: int, low: int) -> Blossom:
    return Blossom(TILL_VALUES["ring"], layouts.ring(high, low))


def bloom(petals: tuple[int, ...]) -> Blossom:
    return Blossom(sips.BLOOM, petals)


def face(schema_bloom: tuple[int, ...], root: Stem | Bough) -> Face:
    return Face(0, Stem(sips.SCHEMA, (bloom(schema_bloom), root)), 0)


def sealed_bloom(card: Face) -> tuple[int, ...]:
    return slurp.bloom_of(slurp.seal(encode_face(card)))


# the readme: the orchard's welcome mat, in philetus's words


def _sentence(kind: str, *words: Blossom) -> Stem:
    phrase = Stem(PASSAGE_VALUES["phrase"], words)
    return Stem(PASSAGE_VALUES[kind], (phrase,))


README_BODY = Stem(
    PASSAGE_VALUES["paragraph"],
    (
        _sentence("exclamation", neem("welcome"), neem("friends")),
        _sentence(
            "exclamation",
            neem("welcome"),
            neem("to"),
            neem("the"),
            neem("gardens"),
            neem("of"),
            prop("karnak"),
        ),
        _sentence(
            "statement",
            neem("meander"),
            neem("along"),
            neem("the"),
            neem("winding"),
            neem("pathways"),
        ),
        _sentence(
            "statement",
            neem("lounge"),
            neem("beneath"),
            neem("the"),
            neem("shade"),
            neem("of"),
            neem("the"),
            neem("trees"),
        ),
        _sentence(
            "statement",
            neem("taste"),
            neem("of"),
            neem("the"),
            neem("ripe"),
            neem("fruits"),
        ),
        _sentence(
            "statement",
            neem("and"),
            neem("sow"),
            neem("the"),
            neem("seeds"),
            neem("for"),
            neem("those"),
            neem("who"),
            neem("will"),
            neem("follow"),
        ),
        # the rooster takes the sign-off
        Stem(
            PASSAGE_VALUES["turn"],
            (_sentence("exclamation", neem("caw-caw")),),
        ),
    ),
)

README_TEXT = (
    "Welcome friends! Welcome to the gardens of Karnak! "
    "Meander along the winding pathways. "
    "Lounge beneath the shade of the trees. "
    "Taste of the ripe fruits. "
    "And sow the seeds for those who will follow. "
    "“Caw-caw!”"
)

# the readme's two faces, under the real mary frances arbor
README_PASSAGE_FACE = face(MF_BLOOMS["passage"], README_BODY)
README_TAPROOT_FACE = face(
    MF_BLOOMS["taproot"],
    Bough(
        TAPROOT_VALUES["taproot"],
        (Blossom(sips.GRAFT, (TAPROOT_VALUES["passage"],)),),
    ),
)


# the eight records


def _till(act: Stem) -> Face:
    return face(DELTA_BLOOMS["till"], act)


def _flush(act: Stem) -> Face:
    return face(DELTA_BLOOMS["flush"], act)


def _plot(name: str) -> Face:
    return _till(Stem(TILL_VALUES["plot"], (neem(name),)))


FOUND = _till(Stem(TILL_VALUES["found"], (neem("karnak"),)))

STAKE = _till(
    Stem(
        TILL_VALUES["stake"],
        (ring(*PROSE_LINEAGE_RING), bloom(MF_BLOOMS["taproot"])),
    )
)

SOW = _flush(
    Stem(
        FLUSH_VALUES["sow"],
        (
            ring(*TAPROOT_RING),
            ring(*PROSE_RING),
            bloom(sealed_bloom(README_TAPROOT_FACE)),
            ring(*README_RING),  # the taproot's one graft: the leaf
        ),
    )
)

SHOOT = _flush(
    Stem(
        FLUSH_VALUES["shoot"],
        (ring(*README_RING), bloom(sealed_bloom(README_PASSAGE_FACE))),
    )
)

# the log: the orchard springs up in its founding second
TILLS = (
    ((FOUNDED, 0), FOUND),
    ((FOUNDED, 1), _plot("plots")),
    ((FOUNDED, 2), _plot("schemas")),
    ((FOUNDED, 3), _plot("gardeners")),
    ((FOUNDED, 4), _plot("prose")),
    ((FOUNDED, 5), STAKE),
)
FLUSHES = (
    ((FOUNDED, 6), SOW),
    ((FOUNDED, 7), SHOOT),
)


def faces() -> dict[str, bytes]:
    """the ten seeded faces, sealed: six schemas, two delta schemas,
    and the readme's taproot and passage."""
    return {
        **mary_frances.sealed(),
        **deltas.sealed(),
        "readme-taproot": slurp.seal(encode_face(README_TAPROOT_FACE)),
        "readme-passage": slurp.seal(encode_face(README_PASSAGE_FACE)),
    }


def seed(backing: Store) -> None:
    """write the genesis through a store: ten faces into the faces
    table, eight records sealed into the logs. byte-reproducible --
    the founding second is fixed and the blooms are deterministic,
    so the golden store is nothing but a fresh seed, verbatim."""
    for data in faces().values():
        backing.put("faces", store.bloom_key(slurp.bloom_of(data)), data)
    for stamp_ring, record in TILLS:
        sealed = slurp.seal(encode_face(record))
        backing.put("tills", store.ring_key(stamp_ring), sealed)
    for stamp_ring, record in FLUSHES:
        sealed = slurp.seal(encode_face(record))
        backing.put("flushes", store.ring_key(stamp_ring), sealed)
