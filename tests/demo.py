"""seed karnak into a filestore, open it, hear it speak: `just run`."""

import tempfile

import genesis

from hwatu import nodes, orchard, slurp, store
from hwatu.codec import parse_face
from hwatu.render import render_face
from hwatu.schema import load


def main() -> None:
    ground = tempfile.mkdtemp(prefix="karnak-")
    backing = store.FileStore(ground)
    genesis.seed(backing)
    karnak = orchard.open(backing)
    print(f"the {karnak.name} orchard, founded {genesis.FOUNDED}")
    print(f"opened from {ground}")
    print("plots: " + ", ".join(karnak.plots.values()))
    print(f"documents: {len(karnak.documents)}; cards: {len(karnak.backs)}")
    print()
    for taproot_ring in karnak.documents:
        for kid in karnak.backs[taproot_ring].kids:
            bloom = karnak.backs[kid].bloom
            data = backing.get("faces", store.bloom_key(bloom))
            assert data is not None
            leaf = parse_face(slurp.unpack(data))
            governor = leaf.root.kids[0]
            assert isinstance(governor, nodes.Blossom)
            speaks_data = backing.get("faces", store.bloom_key(governor.petals))
            assert speaks_data is not None
            speaks = load(slurp.unpack(speaks_data))
            print(render_face(leaf, speaks))


if __name__ == "__main__":
    main()
