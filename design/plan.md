# Implementation Plan

The hwatu prototype's roadmap and status tracker: scope, concrete work items per phase, and open questions. Realigned 2026-07-20 against the settled spec (metastructure, metaschema, glyph table, 60-bit ids); only the active phase is fully fleshed out — later phases stay as stubs until promoted.

Status markers: `[ ]` todo, `[~]` in progress, `[x]` done, `[!]` blocked.

## Prototype scope

Validate the spec end-to-end against the canonical corpus: encode real sip streams, seed real schema cards, ingest chapter 4 of [the Mary Frances Garden Book](https://www.gutenberg.org/cache/epub/53098/pg53098-images.html) as a tree of cards, and render it back as markdown that diffs clean against the source (modulo the decided normalizations). After the flat-yaml prototype settles, we evaluate whether to prototype against a real key-value store in hwatu or move to the Rust implementation in [hanafuda](https://github.com/hexdown/hanafuda).

The fixtures precede the code — the *schema as test suite* lineage, with the hand as the machine's first test. They live in the spec repo: the fully annotated chapter ([ch4-annotation.md](../../spec/design/ch4-annotation.md)), the hand-encoded passage schema ([passage-schema.md](../../spec/design/passage-schema.md)), the six worked schemas ([mary-frances-schemas.md](../../spec/design/mary-frances-schemas.md)), and above all [card3-golden.md](../../spec/design/card3-golden.md) — the hand-spelled card the encoder must reproduce byte-exactly. Tests accompany each work item; the justfile's `test` recipe runs them.

## Current focus

**Phase 1 is complete** (validator landed 2026-07-20; 56 tests green). The complete pipeline runs: canonical bytes → sips → tree → rendered markdown, verified end-to-end in test_seeds — and faces are now judged against their schemas with per-subtree verdicts. Phase 2 (store + orchard) is next: promote its stub to concrete items in a design session before implementation.

The genesis and delta design sessions landed 2026-07-20 ([genesis.md](../../spec/design/genesis.md), [delta-schemas.md](../../spec/design/delta-schemas.md)), and their scaffold arrived ahead of the promotion: `hwatu/deltas.py` (TILL and FLUSH as library schemas — coded, not staked — each sealing to a 96-byte card with its bloom pinned in test_deltas) and the ring layout in `layouts.py` (ten petals, 6+4, with `halves` for work and `pair` for display). And the genesis itself landed the same day (`tests/genesis.py` + `tests/test_genesis.py`, 79 tests green): **the karnak orchard** — founded at the spec repo's first-commit second (1778450399), eight records springing up with counters 0–7, ten seeded faces, the readme document (taproot + passage leaf, 72 + 240 bytes) parsing under the real mary frances arbor and rendering philetus's welcome through the v1 renderer. The hand-coded-genesis gate is passed: the delta design is proven against real sips, unblocking the data-model.md and store.md promotion rewrite. And replay landed (`hwatu/orchard.py` + `tests/test_replay.py` + `tests/demo.py`, 87 tests green): `orchard.open(tills, flushes, faces)` merges the logs by stamp (tills first on ties), dispatches acts by kind name (unknown kinds skip — forward compatible), distills the lean projections (name, plots, registry, documents, backs, allocator; a card's document is the high half of its own ring), replay-assigns plot rings with explicit rings bumping the counters, and checks every planted record's ring tail against its face's grafts when the face is at hand. **`just run` opens karnak from nothing but the log and the seeded faces and prints the readme** — with the passage schema resolved from the faces by bloom, the dynamic-loading story end to end. Remaining phase-2 machinery: the Store protocol + FileStore/SqliteStore engines, seeding a real store with this genesis, `open(store)` = read + parse + replay, and the `hwatu inspect` / `hwatu list` CLI.

Phase 2's substrate direction (2026-07-20): the Store protocol is the contract — `(table, key) → bytes` — shipped with **two engines**, FileStore (yaml, cat-able) and SqliteStore (stdlib, kv-discipline only: no indices or SQL-isms, because redb is the destination), one parametric test suite against both.

The seam ruling (2026-07-20, philetus): **corpus data lives with its corpus, never in the library.** The generic chain-sealing mechanism is `schema.chain()`; the mary frances schema set is a test fixture (`tests/mary_frances.py`) whose destination is data-at-rest — phase 2 seeding writes the schemas as cards, and the sealed bytes export to `corpus/hexdown/` as cross-implementation golden fixtures for hanafuda.

The v1 renderer (`hwatu/render.py`) arrived ahead of its phase-3 slot: sentence-level dialogue mechanics complete and verified against the speech-examples golden walks — card 3 renders from raw sips to `“Caw-caw!” Feather Flop cleared his throat. “Caw-caw!”`. Remaining renderer scope for phase 3: embedded quoths, then the full-chapter pass.

## Phase 1 — metastructure codec, TDD against the golden card

**Goal:** encode and parse real sip streams. Success: card 3 round-trips byte-exactly through the codec, and the six mary frances schema cards encode to real hashes — the moment `⟨#passage⟩` resolves.

- [x] **sips + glyphs module** (`hwatu/sips.py`, 2026-07-20) — sip value constants (octal), the four kind families by leading bits, the glyph table from `spec/glyphs.md` (base-36 petals via `int(c, 36)`; reserved kinds: schema `0o00`, neem `0o74` `·`, graft `0o75`, bloom `0o76`, null `0o77`), glyph ↔ value round-trip
  - Acceptance: every value renders and parses; base-36 petals match `int`/`numpy`-free stdlib conversion; family classification by bit test
- [x] **metastructure codec** (`hwatu/nodes.py` + `hwatu/codec.py`, 2026-07-20) — node tree dataclasses (stem/branch/blossom generic nodes; frozen, tuple children) ↔ sip sequences; the five-line parser (null → pad; ≥`0o60` → petals; ≥`0o40` → children-must-be-grafts; else recurse) plus its inverse
  - Acceptance: parse(encode(tree)) == tree for hand-built trees; parsing never fails on complete streams
  - Notes: tree-sitter-inspired principle — *parse always returns a tree; validation is separate and per-subtree*; truncation diagnostics report exactly what the count sips still expect
  - Architecture (2026-07-20): **no hardcoded content-kind classes** — the only Python types are what every parser must know (metastructure + metaschema); kinds are numbers, semantics arrive as a schema-parameterized *view*, authoring goes through schema-resolved builders. New trellises require zero new Python. The tree is the working form; the slurp bytes remain canonical (they carry the hash).
- [x] **slurp pack/unpack** (`hwatu/slurp.py`, 2026-07-20) — bit-packed 4 sips per 3 bytes; 24-byte increments, 1440-byte max; leading arena / trailing slack beats
  - Acceptance met: 141 content sips pack to a 160-sip / 120-byte slurp with 19 trailing beats, per card3-golden
- [x] **content hashing** (2026-07-20) — blake2b-384 over the slurp bytes (64 petals exactly); collision redistribution (arena shift, growth on exhaustion)
  - Acceptance met: deterministic blooms; redistribution changes the hash while preserving the content
- [x] **the golden card test** (`tests/test_codec.py`, 2026-07-20) — construct card 3's tree in code, encode, compare sip-for-sip and glyph-for-glyph against card3-golden.md
  - Acceptance met: exact match on all 141 sips and the glyph stream (`01*-…·6caw-caw…`), null-hash bloom standing in until the passage schema card is hashed
- [x] **metaschema + schema cards** (`hwatu/schema.py` + `tests/mary_frances.py`, 2026-07-20) — the hardcoded metaschema (trellis root `0o01`, kind `0o02`; specs kids `0o73` / crowns `0o72` / layout `0o71` / grafts `0o70`, one shape per family; single-pass positional values; pads skip by look-ahead); the six mary frances seed schemas hash-chained with **real blooms** — `#passage` resolved (pinned in test_seeds), taproot blooming over all four body kinds, every schema a single card (banner 96B … taproot 312B)
  - Acceptance met — and the seeding caught spec bug #3: banner admitted `prop` without declaring it (prop is conventional, not reserved); fixed in seeds and the spec
- [x] **semantic validator** (`hwatu/validate.py`, 2026-07-20) — walk a tree under its schema, tree-sitter style: a tuple of per-subtree verdicts (path + rule + report), empty meaning valid; the rules: crown at the card root, kids admission, bough children all grafts, graft petals ∈ the bough's grafted set (position kinds globally), reserved arities (graft exactly 1 petal, bloom exactly 64), the face's bloom-and-root silhouette. family agreement needs no rule — the positional seats make it structural
  - Acceptance met: card 3 validates under the passage schema; single-sip mutations of the golden stream yield exactly one verdict at the mutated subtree's path, siblings unimpeached

## Phase 2 — store + orchard

(stub; promoted when phase 1 lands)

- ids: 60-bit ten-petal rings — card rings (36+24) and stamp rings (36+24; hexdown epoch = unix epoch); flat-yaml store per [store.md](store.md) (faces = base64 bit-packed slurps; backs provisionally yaml); plots + metaplot with the realigned defaults (`plots`, `schemas`, `gardeners`, `prose`); bootstrap seeding (six schema cards into `schemas`); `hwatu inspect` (glyph view) and `hwatu list --plot`

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

- may a pad hold a place under a bough (an absent graft slot preserving positional alignment), or does "children must all be grafts" stay strict? the spec reads both ways — encoding.md's pad rule says a pad in a child position is an intentionally empty slot, but the bough family rule is emphatic. the validator currently rules strict (a pad under a bough draws a `family` verdict). ruled 2026-07-20 (philetus): stay strict until gaps in documents earn their keep
- whether the store's `faces` values should also carry a debug glyph rendering alongside the base64 slurp, or leave that entirely to `hwatu inspect` (lean: inspector only — one source of truth)
- hardening: `codec.parse` recurses; a pathological-but-valid card of nested single-child stems reaches depth ~960 in 1920 sips, near python's default 1000-frame limit. real cards are shallow; convert to an explicit-stack iterative parse before hostile input matters (cmu was right at the margin)
- layering (settled 2026-07-20): the codec never interprets petals; `layouts.py` holds the closed set of petal interpretations (phoneme = 0; numeric joins with quant), dispatched by the schema layer per blossom kind. renderer interface: `render(tree, schema) -> markdown`, a rulebook keyed by kind *name*, unknown names degrading gracefully, grafts taking a resolver when branch cards arrive. settled 2026-07-20 (philetus): cards are pure structure, up to the names schemas assign; rendering is a separate renderer, implemented in code, taking the schema-tagged tree — render rules do not become cards.
