# Hwatu Design Docs

A collection of design documents for Hwatu, a prototype embedded card store for managing a corpus of [Hexdown](https://github.com/hexdown/spec) documents.

For the document model, encoding, arbors, and delta semantics that Hwatu implements, see the [Hexdown specification](https://github.com/hexdown/spec). The documents here cover the Python prototype implementation specifically.

- [Vision](vision.md) — role of Hwatu within the Hexdown ecosystem.
- [Store](store.md) — flat-yaml backing store, table layout, durability classes, and the planned migration to a key-value substrate.
- [Plan](plan.md) — roadmap and status tracker: prototype scope, concrete work items per phase, and open questions; updated as implementation proceeds.
- [Style](style.md) — code conventions: absolute imports, modules-as-modules, classes-by-name, no single-letter names.
