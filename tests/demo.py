"""open the karnak orchard and let it introduce itself: `just run`."""

import genesis
from genesis import FLUSHES, TILLS

from hwatu import nodes, orchard, slurp
from hwatu.codec import parse_face
from hwatu.render import render_face
from hwatu.schema import load


def main() -> None:
    karnak = orchard.open(TILLS, FLUSHES, genesis.faces().values())
    seeded = {slurp.bloom_of(data): data for data in genesis.faces().values()}
    print(f"the {karnak.name} orchard, founded {genesis.FOUNDED}")
    print("plots: " + ", ".join(karnak.plots.values()))
    documents = len(karnak.documents)
    print(f"documents: {documents}; cards: {len(karnak.backs)}")
    print()
    for taproot_ring in karnak.documents:
        for kid in karnak.backs[taproot_ring].kids:
            leaf = parse_face(slurp.unpack(seeded[karnak.backs[kid].bloom]))
            governor = leaf.root.kids[0]
            assert isinstance(governor, nodes.Blossom)
            speaks = load(slurp.unpack(seeded[governor.petals]))
            print(render_face(leaf, speaks))


if __name__ == "__main__":
    main()
