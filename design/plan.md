# Implementation Plan

Concrete work items for the hwatu prototype, realigned 2026-07-20 against the settled spec (metastructure, metaschema, glyph table, 60-bit ids). Only the active phase is fully fleshed out; later phases stay as stubs until promoted.

Status markers: `[ ]` todo, `[~]` in progress, `[x]` done, `[!]` blocked.

Tests accompany each item — the justfile's `test` recipe runs them. The golden fixtures live in the spec repo: [ch4-annotation.md](../../spec/design/ch4-annotation.md), [passage-schema.md](../../spec/design/passage-schema.md), [mary-frances-schemas.md](../../spec/design/mary-frances-schemas.md), and above all [card3-golden.md](../../spec/design/card3-golden.md) — the hand-spelled card the encoder must reproduce exactly. The hand is the test for the machine.

## Current focus

Phase 1: slurp pack/unpack (sips + codec landed 2026-07-20, full validation green).

## Phase 1 — metastructure codec, TDD against the golden card

**Goal:** encode and parse real sip streams. Success: card 3 round-trips byte-exactly through the codec, and the six mary frances schema cards encode to real hashes — the moment `⟨#passage⟩` resolves.

- [x] **sips + glyphs module** (`hwatu/sips.py`, 2026-07-20) — sip value constants (octal), the four kind families by leading bits, the glyph table from `spec/glyphs.md` (base-36 petals via `int(c, 36)`; reserved kinds: schema `0o00`, neem `0o74` `·`, graft `0o75`, bloom `0o76`, null `0o77`), glyph ↔ value round-trip
  - Acceptance: every value renders and parses; base-36 petals match `int`/`numpy`-free stdlib conversion; family classification by bit test
- [x] **metastructure codec** (`hwatu/nodes.py` + `hwatu/codec.py`, 2026-07-20) — node tree dataclasses (stem/branch/blossom generic nodes; frozen, tuple children) ↔ sip sequences; the five-line parser (null → pad; ≥`0o60` → petals; ≥`0o40` → children-must-be-grafts; else recurse) plus its inverse
  - Acceptance: parse(encode(tree)) == tree for hand-built trees; parsing never fails on complete streams
  - Notes: tree-sitter-inspired principle — *parse always returns a tree; validation is separate and per-subtree*; truncation diagnostics report exactly what the count sips still expect
  - Architecture (2026-07-20): **no hardcoded content-kind classes** — the only Python types are what every parser must know (metastructure + metaschema); kinds are numbers, semantics arrive as a schema-parameterized *view*, authoring goes through schema-resolved builders. New trellises require zero new Python. The tree is the working form; the slurp bytes remain canonical (they carry the hash).
- [ ] **slurp pack/unpack** — bit-packed 4 sips per 3 bytes; 24-byte increments, 1440-byte max; leading arena / trailing slack beats
  - Acceptance: 141 content sips pack to a 160-sip / 120-byte slurp with 19 trailing beats, per card3-golden
- [ ] **content hashing** — blake2b-384 over the slurp bytes (64 petals exactly); collision redistribution (arena shift, growth on exhaustion)
  - Acceptance: identical trees hash identically; redistribution changes the hash while preserving the parse
- [x] **the golden card test** (`tests/test_codec.py`, 2026-07-20) — construct card 3's tree in code, encode, compare sip-for-sip and glyph-for-glyph against card3-golden.md
  - Acceptance met: exact match on all 141 sips and the glyph stream (`01*-…·6caw-caw…`), null-hash bloom standing in until the passage schema card is hashed
- [ ] **metaschema + schema cards** — the hardcoded metaschema (trellis root `0o01`, kind `0o02`, kids `0o73`, crowns `0o72`, layout `0o71`; positional values: stems ascend `0o01`, boughs descend `0o57`, blossoms descend `0o73`; pads skip seats); schema dataclasses; encode the six mary frances schemas ([mary-frances-schemas.md](../../spec/design/mary-frances-schemas.md)) and compute their real hashes
  - Acceptance: `#passage` and friends resolve to real 384-bit blooms; each schema card parses back under the metaschema to its source definition; the passage schema card lands near its ~264-sip estimate
- [ ] **semantic validator** — walk a face under its schema: kids membership, crown check at the card root, graft petals ∈ the bough's kids, bough-family children are all grafts
  - Acceptance: card 3 validates under the passage schema; mutated streams yield per-subtree verdicts, not global failure

## Phase 2 — store + orchard

(stub; promoted when phase 1 lands)

- ids: 60-bit / ten-petal `CardId` (36+24) and `StampId` (36+24, hexdown epoch TBD); flat-yaml store per [store.md](store.md) (faces = base64 bit-packed slurps; backs provisionally yaml); plots + metaplot with the realigned defaults (`plots`, `schemas`, `gardeners`, `prose`); bootstrap seeding (six schema cards into `schemas`); `hwatu inspect` (glyph view) and `hwatu list --plot`

## Phase 3 — chapter 4 ingest + round-trip

(stub)

- hand-transcribed card trees in `tests/data/` (card-by-card constructors from [ch4-annotation.md](../../spec/design/ch4-annotation.md)); ingest through the orchard API; markdown renderer implementing the dialogue mechanics (quoted-run derivation, softening, derived capitalization, `·`/`^` conventions); round-trip diff against `corpus/markdown/.../chapter-4-feather-flop-s-argument.md`, exact modulo the decided normalizations

## Phase 4 — deltas as card-like faces

(stub; design session first — wanted as soon as schemas and faces parse)

- direction (2026-07-20): tills and flushes are card-like — faces parsed under built-in schemas, stored in the same medium as card faces, **without backs** (a delta with a back would loop); backs become projections computed from flush history; the back record encoding (ten-petal id blossoms, pad-marked absent fields) lands here — sips all the way down completes

## Phase 5 — the markdown transcoder + wider corpus

(stub)

- hexdown-flavored markdown → card trees → store, encoding the interpretation rules learned in the phase-3 hand pass (speech detection, embedded-vs-sentence quoths, normalizations); parser choice open: markdown-it-py (pure python, light) vs tree-sitter-markdown (heavier; hanafuda's design docs already planned tree-sitter for its ingest layer); then ch2 / ch23 / ch47 / front matter, and the corpus-demands features they add (verse, list, lift, note, stress/shout)

## Open questions

- whether the store's `faces` values should also carry a debug glyph rendering alongside the base64 slurp, or leave that entirely to `hwatu inspect` (lean: inspector only — one source of truth)
- hardening: `codec.parse` recurses; a pathological-but-valid card of nested single-child stems reaches depth ~960 in 1920 sips, near python's default 1000-frame limit. real cards are shallow; convert to an explicit-stack iterative parse before hostile input matters (cmu was right at the margin)
- pyproject housekeeping: `Source` URL still points at pentabased/tiraz
