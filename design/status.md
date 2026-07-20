# Status

Hwatu is realigned (2026-07-20) against the settled hexdown spec and ready to implement. The spec gates that blocked the original phasing are all resolved: the metastructure, the metaschema, and the glyph table are settled in [spec/encoding.md](../../spec/encoding.md) and [spec/glyphs.md](../../spec/glyphs.md), and golden fixtures exist before a line of hwatu is written.

- [Vision](vision.md) — role of hwatu within the hexdown ecosystem
- [Store](store.md) — flat-yaml backing store, table layout, durability classes
- [Plan](plan.md) — concrete work items per phase, status tracker, open questions

## First prototype scope

Validate the spec end-to-end against the canonical corpus: encode real sip streams, seed real schema cards, ingest chapter 4 of [the Mary Frances Garden Book](https://www.gutenberg.org/cache/epub/53098/pg53098-images.html) as a tree of cards, and render it back as markdown that diffs clean against the source (modulo the decided normalizations).

The fixtures precede the code: a fully annotated chapter ([ch4-annotation](../../spec/design/ch4-annotation.md)), six worked schemas ([mary-frances-schemas](../../spec/design/mary-frances-schemas.md)), and a hand-spelled golden card ([card3-golden](../../spec/design/card3-golden.md)) the first encoder must reproduce byte-exactly — the *schema as test suite* lineage, with the hand as the machine's first test.

## Phasing

1. **Metastructure codec** — TDD against the golden card; encode + hash the six schema cards (`⟨#passage⟩` resolves); semantic validator with per-subtree verdicts.
2. **Store + orchard** — 60-bit ten-petal ids, flat-yaml store (faces as bit-packed slurps; backs provisionally yaml), plots (`plots`, `schemas`, `gardeners`, `prose`), seeding, CLI inspector.
3. **Chapter 4 round-trip** — hand-transcribed trees in, markdown out, diff against the corpus.
4. **Deltas as card-like faces** — design session then implementation: tills and flushes as faces under built-in schemas, no backs; back records become computed projections. Sips all the way down completes.
5. **The markdown transcoder** — hexdown-flavored markdown straight to the store, encoding the interpretation rules learned by hand; then the wider corpus.

After the flat-yaml prototype settles, we evaluate whether to prototype against a real key-value store in hwatu or move to the Rust implementation in [hanafuda](https://github.com/hexdown/hanafuda).
