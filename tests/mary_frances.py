"""the mary frances schema set: six cards, hash-chained. test fixtures.

schemas are data, and corpus data lives with its corpus, never in the
hwatu library ("hwatu ships no content vocabulary"). this module is
the schema set from spec/design/mary-frances-schemas.md in fixture
form; its destination is data-at-rest -- phase 2 seeding writes these
as cards in the store, and the sealed bytes export to corpus/hexdown/
as cross-implementation golden fixtures for hanafuda to verify.

the chain resolves in dependency order: passage and banner stand
alone; section blooms over them; chapter, book, and the taproot
follow. the taproot omits the at / dex / status meta positions until
those schemas exist.
"""

from hwatu import layouts, slurp
from hwatu.schema import Grafts, Kids, Kind, Layout, Ref, Schema, chain

SENTENCES = ("statement", "question", "exclamation", "broken")

PASSAGE = Schema(
    name="passage",
    crowns=("paragraph",),
    kinds=(
        Kind("paragraph", Kids((*SENTENCES, "turn"))),
        Kind("statement", Kids(("phrase", "pivot", "quoth"))),
        Kind("question", Kids(("phrase", "pivot", "quoth"))),
        Kind("exclamation", Kids(("phrase", "pivot", "quoth"))),
        Kind("broken", Kids(("phrase", "pivot", "quoth"))),
        Kind("turn", Kids((*SENTENCES, "quoth", "fade"))),
        Kind("quoth", Kids(("phrase",))),
        Kind("fade", Kids((*SENTENCES, "phrase"))),
        Kind("phrase", Kids(("neem", "prop"))),
        Kind("pivot", Kids(("neem", "prop"))),
        Kind("prop", Layout(layouts.PHONEME)),
    ),
)

BANNER = Schema(
    name="banner",
    crowns=("title",),
    kinds=(
        Kind("title", Kids(("neem", "prop", "quant"))),
        Kind("prop", Layout(layouts.PHONEME)),
        Kind("quant", Layout(layouts.NUMERIC)),
    ),
)

SECTION = Schema(
    name="section",
    crowns=("section",),
    kinds=(
        Kind("banner", Ref("banner")),
        Kind("passage", Ref("passage")),
        Kind("section", Grafts(("banner", "passage"))),
    ),
)

CHAPTER = Schema(
    name="chapter",
    crowns=("chapter",),
    kinds=(
        Kind("banner", Ref("banner")),
        Kind("section", Ref("section")),
        Kind("chapter", Grafts(("banner", "section"))),
    ),
)

BOOK = Schema(
    name="book",
    crowns=("book",),
    kinds=(
        Kind("banner", Ref("banner")),
        Kind("chapter", Ref("chapter")),
        Kind("book", Grafts(("banner", "chapter"))),
    ),
)

TAPROOT = Schema(
    name="taproot",
    crowns=("taproot",),
    kinds=(
        Kind("book", Ref("book")),
        Kind("chapter", Ref("chapter")),
        Kind("section", Ref("section")),
        Kind("passage", Ref("passage")),
        Kind("taproot", Grafts(("book", "chapter", "section", "passage"))),
    ),
)

# dependency order: every Ref target precedes its referrer
SCHEMAS = {
    "passage": PASSAGE,
    "banner": BANNER,
    "section": SECTION,
    "chapter": CHAPTER,
    "book": BOOK,
    "taproot": TAPROOT,
}


def sealed() -> dict[str, bytes]:
    """every mary frances schema as canonical slurp bytes."""
    return chain(SCHEMAS)


def blooms() -> dict[str, tuple[int, ...]]:
    """name -> the 64 petals of each schema's content hash."""
    return {name: slurp.bloom_of(data) for name, data in sealed().items()}
