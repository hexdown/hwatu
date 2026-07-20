# realignment briefing — hwatu meets the settled spec

session-prep for revising these design docs against the spec as it stands after the 2026-07-18/19 design stretch. this doc is an *agenda with leans*, not a plan — the decisions belong to the morning conversation. it dies once [plan.md](plan.md) and [store.md](store.md) are revised.

## what changed under hwatu's feet

while hwatu slept, the spec settled: the metastructure (uniform kind+count nodes, stem/blossom families by high bit, reserved kinds, schema node opening every face), the metaschema (trellis root, two-child kind nodes, positional values, kids/crowns/layout/bloom specs), the glyph table, the speech stems, and the arbor's dissolution into taproot-trellis closures. and hwatu gained fixtures it never planned for: a fully annotated chapter ([spec/design/ch4-annotation.md](../../spec/design/ch4-annotation.md)), six worked schemas ([spec/design/mary-frances-schemas.md](../../spec/design/mary-frances-schemas.md)), and a golden card hand-spelled to 141 exact sips ([spec/design/card3-golden.md](../../spec/design/card3-golden.md)).

## stale-audit

**[plan.md](plan.md)** — the deep one:

- *"placeholder serialization (yaml-in-bytes)"* — *obsoleted.* the real codec is a ~20-line parser plus its inverse, and a golden card exists to test it against. phase 2 ("concrete sip-stream encoding") collapses into phase 1.
- *"document-node dataclasses (passage-trellis subset)"* — kind list predates the speech session: no turn, quoth, pivot, broken, fade; span's role has narrowed (kind-mixing compounds only; beat joins homogeneous ones).
- *"bough and graft dataclasses"* — grafts are now one-petal blossom-family nodes, not single sips.
- *"trellis and arbor dataclasses ... hardcoded python objects"* — schemas are now *cards* with a settled encoding; only the metaschema is hardcoded. seeding = encoding the six mary frances schema cards and computing their real hashes (the moment `⟨#passage⟩` resolves — the first bloom blooms).
- *"test-script ingest"* — the source material is now the ch4 annotation itself.
- *"basic text reader"* — can aim higher: the render rules (dialogue mechanics, softening, derived caps) are settled, so markdown-out and a diff against the corpus source is a real acceptance test.
- survives intact: id/hash primitives, card/face/back dataclasses, flat-yaml store, orchard wiring, CLI inspector.

**[store.md](store.md)** — mostly weathered well:

- `report` plot → `prose`; `spec/metaschema.md` references → `spec/encoding.md`
- slurps *validated* by the golden card (141 content sips → one 160-sip / 120-byte slurp)
- back's `trellis_ref` survives as the stable-id index under the two-coordinate pattern (truth = face's schema bloom)
- the `arbors` + `trellises` default plots predate the dissolution — see decision 2

**[status.md](status.md) / [vision.md](vision.md)** — light touches: metaschema references, report→prose, phasing summary.

## the morning's decisions

1. **the new phase ladder.** lean: phase 1 becomes codec-first TDD — (a) metastructure codec vs the golden card, (b) encode + hash the six schemas, (c) dataclasses + store, (d) ch4 ingest from the annotation, (e) markdown render + round-trip diff. everything else shuffles behind it.
2. **default plots.** with the arbor dissolved, do `arbors` + `trellises` merge into one `schemas` plot? (lean: yes.) does `chat` stay seeded or defer? (lean: defer.)
3. **id width.** hwatu must pick a provisional: 64-bit as data-model currently specs, or the 60-bit / 10-petal candidate from the sips-all-the-way-down question. (lean: 60-bit — phase 1 is the cheapest moment this choice will ever have.)
4. **byte packing.** bit-packed 4-sips-per-3-bytes, per the slurp design? (lean: yes; the alignment sentence in encoding.md already assumes it.)
5. **backs.** the back/delta record encoding is the one big *undesigned* region. lean: faces real sips from day one, backs provisionally yaml — the honest split between settled and unsettled — with the back encoding designed when deltas arrive (phase 3), where the id-width and absence-pad decisions land together.
6. **ingest mechanics.** hand-transcribe the ch4 trees into test constructors, or parse the annotation doc's notation? (lean: transcribe card-by-card — the annotation stays a document, the tests stay explicit; revisit if it's tedious beyond card 5.)

## readiness

python 3.14.4 ✓ · just 1.45 ✓ · `.venv` present from before the hiatus · pyproject nit to fix in passing: `Source` still points at pentabased/tiraz

sleep well; the fixtures will keep. 🐓
