# Status

Hwatu is in early design development. The first prototype is taking shape across these design docs:

- [Vision](vision.md) — role of hwatu within the hexdown ecosystem
- [Store](store.md) — flat-yaml backing store, table layout, durability classes
- [Plan](plan.md) — concrete work items per phase, status tracker, open questions

## First prototype scope

The goal of the first hwatu prototype is to validate the spec's document tree model end-to-end against a small canonical corpus before the spec is firmed up enough to implement in Rust.

Concretely, success means:

- Python dataclasses for the spec's structural objects (orchard, plot, card, face, back, arbor, trellis, document-node kinds)
- A flat-yaml-backed store laid out per [store.md](store.md)
- A markdown ingestion path that converts a few canonical documents from [the Mary Frances Garden Book](https://www.gutenberg.org/cache/epub/53098/pg53098-images.html) into trees of cards in the store
- A render path that pulls those documents back out of the store and produces equivalent markdown
- A CLI for inspecting records and walking the orchard

## Phasing

The prototype lands in stages so each stage produces something testable:

1. **Document model + flat-yaml store + ingest one document.** Skips deltas (write cards directly), uses placeholder serialization for values. Validates the dataclass shapes and the round-trip.
2. **Concrete sip-stream encoding for faces and backs.** Replaces placeholder serialization with the metaschema-record byte layout. Forces the spec's encoding TBDs to resolve.
3. **Deltas as source of truth.** Adds `flushes` / `tills`; cards become writable only through deltas; backs become projections.
4. **Wider corpus.** Ingest several Mary Frances documents to stress-test the document model and surface spec gaps.

After the flat-yaml prototype settles, we will evaluate whether to also prototype against a real key-value store in hwatu, or jump straight to the Rust implementation in [hanafuda](https://github.com/hexdown/hanafuda).

## Open work in the spec that gates this prototype

- Concrete metaschema record encoding (`spec/metaschema.md` — gate to phase 2)
- Concrete sip-glyph mapping (`spec/encoding.md` — gate to phase 2)
- Full trellis and arbor definitions for the report arbor (`spec/core-arbors.md`)
