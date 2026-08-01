"""karnak on disk: seed a store, open it, the same orchard returns.

open(store) is read + parse + replay -- the projections must equal
the in-memory replay's exactly, the readme must render with every
face resolved through the store, and seeding must be
byte-reproducible: the golden store in the corpus repo is nothing
but a fresh seed, verbatim.
"""

from pathlib import Path

import genesis
import pytest
from genesis import FLUSHES, TILLS

from hwatu import nodes, orchard, slurp, store
from hwatu.codec import parse_face
from hwatu.render import render_face
from hwatu.schema import load
from hwatu.store import Store

GOLDEN = Path(__file__).parents[2] / "corpus" / "hexdown" / "karnak"


@pytest.fixture(params=["file", "sqlite"])
def backing(request: pytest.FixtureRequest, tmp_path: Path) -> Store:
    if request.param == "file":
        seeded: Store = store.FileStore(tmp_path / "ground")
    else:
        seeded = store.SqliteStore(tmp_path / "ground.db")
    genesis.seed(seeded)
    return seeded


def test_an_opened_store_equals_the_replayed_log(backing: Store):
    replayed = orchard.replay(TILLS, FLUSHES, genesis.faces().values())
    assert orchard.open(backing) == replayed


def test_the_readme_renders_through_the_store(backing: Store):
    karnak = orchard.open(backing)
    taproot = karnak.backs[(0, 0)]
    leaf = karnak.backs[taproot.kids[0]]
    data = backing.get("faces", store.bloom_key(leaf.bloom))
    assert data is not None
    leaf_face = parse_face(slurp.unpack(data))
    governor = leaf_face.root.kids[0]
    assert isinstance(governor, nodes.Blossom)
    speaks_data = backing.get("faces", store.bloom_key(governor.petals))
    assert speaks_data is not None
    speaks = load(slurp.unpack(speaks_data))
    assert render_face(leaf_face, speaks) == genesis.README_TEXT


def _tree(ground: Path) -> dict[str, bytes]:
    return {
        str(record.relative_to(ground)): record.read_bytes()
        for record in sorted(ground.rglob("*"))
        if record.is_file()
    }


def test_reseeding_the_same_ground_is_nothing(backing: Store):
    genesis.seed(backing)  # a second seed re-puts identical bytes
    replayed = orchard.replay(TILLS, FLUSHES, genesis.faces().values())
    assert orchard.open(backing) == replayed


def test_seeding_is_byte_reproducible(tmp_path: Path):
    genesis.seed(store.FileStore(tmp_path / "first"))
    genesis.seed(store.FileStore(tmp_path / "second"))
    assert _tree(tmp_path / "first") == _tree(tmp_path / "second")


@pytest.mark.skipif(
    not GOLDEN.exists(), reason="corpus not checked out beside hwatu"
)
def test_the_golden_store_is_a_fresh_seed_verbatim(tmp_path: Path):
    genesis.seed(store.FileStore(tmp_path / "fresh"))
    assert _tree(tmp_path / "fresh") == _tree(GOLDEN)
