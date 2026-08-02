"""the phase-3 capstone: chapter 4 planted whole and read back.

sow the 24-card seedling into temporary stores seeded with the
karnak genesis, reopen, and render the document from its taproot.
the expected text is the hand transcription itself (ruled
2026-08-01: chapter_4's expected strings are the source of truth
for this iteration -- the corpus stays upstream, and measuring how
faithfully renders align with it belongs to the markdown tool's
scoring suite to come).
"""

from pathlib import Path

import genesis
import pytest
from data import chapter_4

from hwatu import orchard, store
from hwatu.orchard import Seedling
from hwatu.render import render_document
from hwatu.store import Store

PROSE_PLOT = genesis.PROSE_RING
SOW_STAMP = genesis.FOUNDED + 0o10  # the ruled test epoch

EXPECTED = (
    "\n\n".join(
        [
            "## " + chapter_4.BANNER_RENDERED,
            *(
                chapter_4.RENDERED[number]
                for number in sorted(chapter_4.RENDERED)
            ),
            "---",
        ]
    )
    + "\n"
)


def seedling() -> Seedling:
    """the whole chapter as one seedling, kids in graft order."""
    passages = tuple(
        Seedling(chapter_4.CARDS[number]())
        for number in sorted(chapter_4.CARDS)
    )
    section = Seedling(
        chapter_4.section_card(),
        (Seedling(chapter_4.banner()), *passages),
    )
    return Seedling(chapter_4.taproot_card(), (section,))


@pytest.fixture(params=["file", "sqlite"])
def backing(request: pytest.FixtureRequest, tmp_path: Path) -> Store:
    if request.param == "file":
        ground: Store = store.FileStore(tmp_path / "ground")
    else:
        ground = store.SqliteStore(tmp_path / "ground.db")
    genesis.seed(ground)
    return ground


def test_chapter_4_round_trips(backing: Store):
    grove = orchard.open(backing)
    taproot = orchard.sow(backing, grove, PROSE_PLOT, seedling(), SOW_STAMP)
    assert taproot == (1, 0)
    assert grove.next_document == 2

    # the grove in hand equals a fresh open of the store
    assert orchard.open(backing) == grove

    def fetch(bloom: tuple[int, ...]) -> bytes | None:
        return backing.get("faces", store.bloom_key(bloom))

    assert render_document(grove, taproot, fetch) == EXPECTED


def test_the_chapter_lives_beside_the_readme(backing: Store):
    grove = orchard.open(backing)
    orchard.sow(backing, grove, PROSE_PLOT, seedling(), SOW_STAMP)
    assert grove.documents == {(0, 0): PROSE_PLOT, (1, 0): PROSE_PLOT}
    assert len(grove.backs) == 2 + 24  # the readme's cards + chapter 4's
