# Store

Hwatu's first prototype backs its card store with a directory of flat YAML files. The layout is shaped by two commitments:

- **Everything is a card.** Arbors, trellises, plot definitions, and gardeners are stored as cards, not as bespoke records. Only four record kinds live below the card layer.
- **Storage substrate is dumb.** The yaml files hold opaque base64-encoded byte values; the storage layer never parses hexdown semantics. The same byte payloads will land directly in a key-value substrate when the prototype graduates.

## Why flat YAML first

A real key-value store (redb, LMDB) is the eventual destination. But for the first prototype we want:

- **Fast iteration** — change record formats without schema migrations
- **Human inspectability** — read a record by `cat`-ing a file
- **No external dependencies** — `./store/` is self-contained and trivial to wipe and recreate
- **Clean migration path** — the layout already thinks in `(table, key) → bytes`, so swapping the substrate is a substrate change, not a shape change

## On-disk layout

```
./store/
├── faces/
│   └── {content-hash}.yaml
├── backs/
│   └── {card-id}.yaml
├── flushes/
│   └── {stamp-id}.yaml
└── tills/
    └── {stamp-id}.yaml
```

Four directories — one per orchard-level table. Each `{table}/{key}.yaml` is one record; the filename carries the key, the directory implies the table.

Everything else — arbors, trellises, plot definitions, gardeners, user documents — lives inside these four tables as cards (face + back pairs). To list the arbors in the orchard, you walk the metaplot's grafts and resolve each to a card in `backs/`.

## Record envelope

```yaml
hexdown-version: 0.1
table: faces
key: <content-hash>
value: |
  <base64-encoded bytes>
```

Self-describing — a record file pulled out of context still names its table and key. The `hexdown-version` field lets the prototype evolve without breaking older fixtures.

## Value encoding

`value` is the base64 encoding of the raw bytes that will eventually live in the key-value store. Those bytes are a packed sip stream (6-bit sips aligned to system word boundaries) organized as a **slurp**.

### Slurps

A **slurp** is a contiguous block of serialized sips with a variable size in **24-byte increments** (32 sips per increment, 3 × 64-bit words / 6 × 32-bit words). Each stored value occupies exactly one slurp.

- **Minimum slurp size: 24 bytes** (one increment, 32 sips)
- **Maximum slurp size: 1440 bytes** (60 increments, 1920 sips) — chosen so a slurp fits in a typical network packet payload after IPv6 + TCP header overhead (60 bytes off a 1500-byte Ethernet MTU)

Within a slurp:

- **Leading `beat` sips** — collision-resolution arena for content-addressed face hashes (per the metastructure in `spec/encoding.md`); skipped by the parser at start-of-stream
- **Content sips** — the actual encoded value
- **Trailing `beat` sips** — slack within the slurp's chosen size; skipped by the parser at end-of-stream

The same `beat` sip (value 0x00, rendered as `-`) serves both roles; the parser distinguishes them by position. The hash is computed over the entire slurp byte stream, so changing the leading-vs-trailing null split changes the hash.

### Collision resolution via slurp growth

The slurp size *is* the collision-resolution budget. When a content hash collides with an existing value:

1. **Redistribute existing nulls** — push one `beat` from the trailing slack to the leading arena, shifting the content one sip rightward within the slurp. The hash changes (because byte positions of the content shift); the slurp size stays the same.
2. **Grow on exhaustion** — if all trailing slack has already been moved forward and the collision still stands, grow the slurp by one 24-byte increment. The new increment lands as trailing beats, opening 32 fresh sips of arena to redistribute.
3. **Repeat** until the collision resolves or the slurp hits its maximum size.

### Records larger than one slurp

A value whose content cannot be encoded into a single slurp at the maximum size (1920 sips total — content plus collision arena) is **rejected** at the storage layer. The arbor / trellis structure is responsible for fragmenting oversized content into multiple cards further up the tree.

This is the strict default and matches the spec's *modest data model* commitment: fragmentation responsibility belongs to the participant shaping the document, not to the storage layer quietly chunking values. Open to revisiting if importing real corpora regularly produces oversized cards.

### Why opaque base64

Keeping `value` opaque has two virtues:

- The store doesn't leak hexdown structure into the storage format
- Migration to a key-value store is a substrate change, not a representation change — the same bytes go in the same way

The trade-off is that base64 isn't human-readable. The mitigation is a CLI inspector (see below).

## Orchard-level tables

| Table | Key | Holds |
|:--|:--|:--|
| `faces` | content-hash | content-addressed face sip stream |
| `backs` | card-id | materialized back record (cache; rebuildable from flushes) |
| `flushes` | stamp-id | append-only content delta |
| `tills` | stamp-id | append-only structural delta |

Note that `flushes` and `tills` share the same key shape (`StampId`) but live in different tables — the table provides the namespace, so a stamp-id of `(stamp=X, counter=Y)` in `flushes` is a different record from the same stamp-id in `tills`. The general principle: **each table has its own id space, even when id shapes are shared across tables.**

## Plots and the metaplot

A **plot** is a logical grouping of cards in the orchard — a unit that gardener permissions attach to and that organizes cards by intent. Each card's back carries a `plot_ref` indicating which plot it belongs to.

Plots are themselves cards. A **plot-definition card** describes one plot (its name, the trellis(es) cards in this plot conform to, recommended meta, etc.). All plot-definition cards live in the **metaplot** — a reflexive plot whose contents are plot-definition cards, including the card describing the metaplot itself.

Default plots seeded in a fresh orchard (realigned 2026-07-20):

- **`plots`** — the metaplot itself; holds plot-definition cards for every plot including its own
- **`schemas`** — holds schema cards (each card's face parsed under the hardcoded metaschema, marked by the null hash); the former `arbors` + `trellises` plots merged when the arbor dissolved into the taproot's trellis
- **`gardeners`** — holds gardener cards (identity + permissions)
- **`prose`** — holds user documents anchored by the prose taproot trellis

(the `chat` plot — text-message-sized DMs under a message-stream arbor — is deferred until a chat schema exists; not critical path.)

Listing cards in a plot is a query: walk the metaplot's grafts to find the plot-definition card, then list all cards whose back's `plot_ref` matches that plot's card-id. The CLI inspector exposes this as `hwatu list --plot <name>`.

Note: "metaplot" is reserved for plots that are reflexive in this way (a plot of plot-definition cards, including its own). The `gardeners` plot is a regular plot — its cards describe gardeners, not other plots — even though it carries orchard infrastructure. Same goes for `schemas` and any other infrastructure plot.

## Durability classes

The spec's [vision](../../spec/vision.md) commits to deltas as the source of truth and other state as ephemeral projections. The store layout reflects three durability classes:

- **Content-addressed (immutable)** — `faces`. Once written, never modified. Keyed by hash; deduplicated automatically across cards that share content.
- **Append-only (immutable)** — `flushes`, `tills`. Each delta is written once and never modified. The full history of every change is reachable by walking these tables.
- **Materialized projections (cache)** — `backs`. Current-state lookups maintained for fast access, but always regenerable from the flush history. Includes the backs of cards that themselves carry orchard infrastructure (arbor cards, trellis cards, plot-definition cards, gardener cards).

## Backs as in-memory dataclasses

Within hwatu, backs are Python dataclasses with the spec's structural fields:

```python
@dataclass
class Back:
    card_id: CardId                       # (document_id, local_id)
    trellis_ref: CardId                   # which trellis governs the face
    plot_ref: CardId                      # which plot the card belongs to
    face_hash: ContentHash                # content hash of the face sip stream
    arbor_ref: CardId | None              # taproot cards only
    child_card_refs: tuple[CardId, ...]   # graft slots in the face
```

The `trellis_ref` and `arbor_ref` fields are stable-id *indexes* under the two-coordinate pattern — the truth is each face's schema bloom and its closure. For the first prototype, backs serialize as provisional yaml (the honest split: faces are real sips from day one, backs wait). The lasting design direction (2026-07-20): **tills and flushes are card-like** — faces parsed under built-in schemas, stored in the same medium as card faces, *without backs* (a delta with a back would loop) — and backs become projections computed from flush history, encoded with ten-petal id blossoms and pad-marked absent fields. That design session comes as soon as schemas and faces parse (plan phase 4); sips all the way down completes there.

## CLI inspector

A small `hwatu inspect` command reads a record and prints a human-readable decoding of the value:

```
$ hwatu inspect store/backs/000000000001_000000.yaml
table: backs
key: (1, 0)   # document_id=1, local_id=0
value (decoded as taproot back):
  card-id: (1, 0)
  trellis-ref: (0, 14)       # prose taproot schema (stable-id index; the face's bloom is the truth)
  plot-ref: (0, 12)          # prose plot
  arbor-ref: (0, 14)         # index to the anchoring schema
  child-card-refs:
    - (1, 1)                 # book branch card
```

A companion `hwatu list --plot <name>` command lists the cards in a plot by walking the metaplot:

```
$ hwatu list --plot schemas
- (0, 14)  taproot
- (0, 15)  book
- (0, 16)  chapter
- (0, 17)  section
- (0, 18)  passage
- (0, 19)  banner
```

The inspector is the canonical way to read a value's structure; the base64 in the record file remains the source-of-truth representation.

## Migration to a key-value substrate

When the prototype is ready to graduate, the substrate swap is:

1. Pick a key-value store (redb, LMDB, ...)
2. Open one named sub-database per orchard-level table (faces, backs, flushes, tills)
3. For each table, the key becomes the kv key and the value's base64-decoded bytes become the kv value

The `hexdown-version` and table/key envelope fields drop away — the table is implied by the sub-database and the key is implied by the kv key. Plot organization stays the same — it's a card-level concept, not a storage-layer one.

## Open questions

- Whether the hwatu API operates on real (provisional) sip-encoded bytes from phase 1, or on placeholder bytes (e.g., yaml-as-bytes) with real sip encoding deferred to phase 2
- Whether to reconsider record chunking across multiple slurps if real corpora regularly produce oversized cards (current default: reject; arbor structure handles fragmentation upstream)
