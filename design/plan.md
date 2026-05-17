# Implementation Plan

Concrete work items for the hwatu prototype, organized by the phases in [status.md](status.md). Only the active phase is fully fleshed out; later phases stay as stubs until promoted.

Status markers: `[ ]` todo, `[~]` in progress, `[x]` done, `[!]` blocked.

Tests accompany each item — the justfile's `test` recipe runs them.

Example documents for ingest live in the [hexdown/corpus repo](https://github.com/hexdown/corpus) at `~/work/hexdown/corpus/`, with vendored HTML under `vendor/` and hand-converted markdown under `markdown/`. The first prototype's ingest target is one chapter from `markdown/the-mary-frances-garden-book-by-jane-eayre-fryer/`.

## Current focus

(none yet — first item starts when implementation begins)

## Phase 1 — Document model + flat-yaml store + ingest one document

**Goal:** validate the dataclass shapes and the end-to-end round-trip with placeholder serialization. Skips deltas (cards are written directly). Reaches success when one Mary Frances chapter ingests through the hwatu API, persists, reads back, and re-renders as human-readable text.

### Work items

- [ ] **ID and hash primitives** — `SequenceId` (monotonic counter), `CardId` (composite: 40-bit document_id + 24-bit local_id, both `SequenceId`s, packed into 64 bits), `StampId` (composite: 40-bit stamp + 24-bit counter, packed into 64 bits — used for both flush-ids and till-ids), `ContentHash` (blake2b digest wrapper)
  - Acceptance: composite ids round-trip through their packed 64-bit form; `SequenceId`s mint monotonically per allocator
  - Notes: each table has its own id space — `StampId` is reused across the `flushes` and `tills` tables; the table provides the namespace, the type provides the shape

- [ ] **Document-node dataclasses (passage-trellis subset)** — `Petal`; `Blossom` kinds `neem` and `prop`; `Stem` kinds `span` / `phrase` / `statement` / `question` / `exclamation` / `title` plus passage-level stems (`paragraph`, `list`, `point`, `quote`, `note`)
  - Acceptance: one Mary Frances paragraph constructs as a tree of these dataclasses in pure Python
  - Notes: defer `quant` / `enum` / `uniglyph` blossoms and `diagram` / `photo` trellises to later phases; the encapsulating rule is **no bough nodes on leaf cards** — a branch card can graft to a stem, but the body of any stem (and the blossoms and petals it contains) always lives on a leaf card

- [ ] **Bough and Graft dataclasses** — `Bough` is a branch-trellis face root; its children are `Graft` slots, each a single sip whose kind value names the kind of child card at that position (resolved through the back's `child_card_refs` to a `CardId`)
  - Acceptance: a `book` bough with chapter `Graft` children constructs correctly; `Graft.kind` matches the kind of the grafted leaf card's face root

- [ ] **Card / face / back dataclasses** — `Card` (face + back), `Face` (wraps a root document node), `Back` (per [store.md](store.md)'s definition — includes `plot_ref` alongside the other structural fields)
  - Acceptance: a single leaf card constructs with a face hash that matches the hash of its serialized face

- [ ] **Trellis and arbor dataclasses** — `Trellis` (branch | leaf flavor, valid node kinds defined inline, head/body structure), `Arbor` (positions + trellis references); node-kind descriptions are fragments of the trellis they live in (no separate node-kind schema)
  - Acceptance: the report arbor and its core trellises (taproot, book, chapter, section, passage, banner) constructible as hardcoded Python objects

- [ ] **Plot and plot-definition dataclasses** — `Plot` (logical grouping; cards point to it via `plot_ref`), `PlotDefinition` (a card face describing one plot, lives in the metaplot)
  - Acceptance: a plot-definition can be constructed for each of the seeded default plots (`plots`, `arbors`, `trellises`, `gardeners`, `report`, `chat`); the metaplot's plot-definition refers to itself as expected

- [ ] **Placeholder serialization** — `Face` / `Back` / plot definitions / arbors / trellises ↔ bytes via a temporary YAML-in-bytes encoding; values padded with trailing `beat` (0x00) sips to the next 24-byte boundary; face hash computed over the padded byte stream
  - Acceptance: round-trip of each dataclass kind through bytes is lossless; identical objects produce identical hashes; all stored values are 24-byte aligned
  - Notes: replaced wholesale in phase 2 with a real sip stream

- [ ] **Flat-yaml store** — `Store` class with `.read(table, key) -> bytes` and `.write(table, key, bytes) -> None`; four orchard-level tables (`faces`, `backs`, `flushes`, `tills`); record envelope (`hexdown-version` / `table` / `key` / `value`); base64 value encoding; directory layout per [store.md](store.md)
  - Acceptance: write a record, read it back, decoded bytes match; on-disk yaml is human-readable with the value as a base64 block

- [ ] **Orchard wiring** — `Orchard` class holding a `Store`, methods to mint card-ids and stamp-ids, sow new cards into plots, resolve trellis / arbor / plot refs, and walk the metaplot to enumerate plots
  - Acceptance: cards written through the orchard land in the right tables; card-ids allocated sequentially per document; the metaplot can be walked from a cold start to find every plot

- [ ] **Bootstrap seeding** — code that initializes a fresh orchard with the seeded default plots (`plots` metaplot, `arbors`, `trellises`, `gardeners`, `report`, `chat`), the core trellises (taproot, book, chapter, section, passage, banner), and the report arbor
  - Acceptance: after seeding, the metaplot lists all default plots; the arbors plot contains the report arbor card; the trellises plot contains the core trellis cards

- [ ] **CLI inspector** — `hwatu inspect <path>` reads a record file and prints a decoded view; dispatches on `table` to pick the right decoder; companion `hwatu list --plot <name>` lists cards in a plot by walking the metaplot
  - Acceptance: human-readable output for `faces`, `backs`, `flushes`, `tills` records; plot listings show the cards in each default plot

- [ ] **Test-script ingest** — hand-written test script that exercises the hwatu API directly to insert a Mary Frances chapter as a card tree (branch cards in the report arbor, leaf passages with stem/blossom/petal trees); no markdown parsing in hwatu itself
  - Acceptance: after the script runs, the store contains the expected card count under the `report` plot; the taproot's `child_card_refs` walk into the document's branch hierarchy

- [ ] **Basic text reader** — walks a card tree from a taproot card-id and emits human-readable text (not full markdown); likely shares decoding helpers with the CLI inspector
  - Acceptance: the rendered text preserves the meaningful content of the test-script-ingested chapter

### Open questions (phase 1)

- Cold-start bootstrap: which well-known card-id locates the metaplot? Likely `(0, 0)` (document_id=0 reserved per the spec; local_id=0 is always the taproot), but worth pinning down.
- Whether the bootstrap trellises (metatrellis, metarbor) are stored as cards in the `trellises` plot from day one, or only their grammars exist (hardcoded in the parser) until phase 2
- Whether the `chat` arbor needs its own definition in phase 1, or if `report` alone is enough for the first prototype
- How to handle the recursive plot-definition card for the metaplot itself (chicken-and-egg between the metaplot and its own plot-definition card — likely resolved by a small hardcoded bootstrap step)

## Phase 2 — Concrete sip-stream encoding

(deferred until phase 1 lands; populated when promoted)

## Phase 3 — Deltas as source of truth

(deferred)

## Phase 4 — Wider corpus

(deferred)
