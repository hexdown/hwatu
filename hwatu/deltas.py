"""the delta schemas: till and flush, the protocol's own vocabulary.

corpus schemas live with their corpus; protocol schemas live here, in
the library -- the seam ruling's contrapositive. tills create an
orchard's presuppositions: founding it, breaking ground on plots,
staking schema lineages to their taproot blooms. flushes operate
within documents: sowing taproots, shooting cards (a shoot at a fresh
ring births a card; at the same ring, replaces its face). one act per
record, the act's kind wearing the crown.

coded, not staked: these schemas are sealed at genesis and their
faces seeded into the orchard, but their authority comes from the
spec's vocabulary, never from the log. replay resolves records
through the hash-keyed faces table and dispatches on kind names, so
the vocabulary can grow without stranding older parsers. blooms are
regression fixtures (pinned in tests), not protocol constants. per
spec/design/delta-schemas.md.
"""

from hwatu import layouts, slurp
from hwatu.schema import Kids, Kind, Layout, Schema, chain

TILL = Schema(
    name="till",
    crowns=("found", "plot", "stake"),
    kinds=(
        Kind("found", Kids(("neem",))),  # the orchard's name
        Kind("plot", Kids(("neem",))),  # break ground: plot name
        Kind("stake", Kids(("ring", "bloom"))),  # lineage ring, taproot bloom
        Kind("ring", Layout(layouts.RING)),
    ),
)

FLUSH = Schema(
    name="flush",
    crowns=("sow", "shoot"),
    kinds=(
        # sow: taproot ring, plot ring, face bloom
        Kind("sow", Kids(("ring", "bloom"))),
        # shoot: card ring, face bloom, child ring per graft in face order
        Kind("shoot", Kids(("ring", "bloom"))),
        Kind("ring", Layout(layouts.RING)),
    ),
)

SCHEMAS = {"till": TILL, "flush": FLUSH}


def sealed() -> dict[str, bytes]:
    """both delta schemas as canonical slurp bytes."""
    return chain(SCHEMAS)


def blooms() -> dict[str, tuple[int, ...]]:
    """name -> the 64 petals of each delta schema's content hash."""
    return {name: slurp.bloom_of(data) for name, data in sealed().items()}
