# Vision

Hwatu is an embedded card store for managing a corpus of [Hexdown](https://github.com/hexdown/spec) documents. This library serves as a building block for the development of tools and applications that work with Hexdown documents. The name "Hwatu" is derived from the Korean "flower battle" deck as a visual reference to the way Hexdown represents documents as collections of cards featuring blossom glyphs and a nod to the [wicked problems](https://en.wikipedia.org/wiki/Wicked_problem) of initial prototype development.

## Role within the hexdown ecosystem

Hwatu is the Python reference implementation of the hexdown spec. It is intended to be the first working implementation of the spec, used to validate design decisions and surface gaps in the specification before they are locked in. Once hwatu has stabilized a model that ingests, stores, and round-trips a meaningful corpus, the same design lands as a production implementation in [hanafuda](https://github.com/hexdown/hanafuda) (Rust over redb).

The two-implementation arc — prototype in Python, production in Rust — borrows directly from the pentabased project that hexdown descends from, where the Python implementation served as a *schema as test suite* reference against which other implementations could be checked.

For the document model, encoding, arbors, and delta semantics that Hwatu implements, see the [Hexdown specification](https://github.com/hexdown/spec).
