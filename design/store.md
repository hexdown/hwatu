# Store

Hwatu's store implements the level-0 half of the spec's two-level architecture ([spec store.md](../../spec/store.md)): three tables of bytes under sorted byte keys, with every hexdown semantic living above it in the orchard api. Two commitments shape everything here:

- **Everything durable is faces plus deltas.** Three tables — `faces`, `tills`, `flushes`. Backs, the plot table, the schema registry, and the id allocator are replay projections and never touch disk.
- **The storage substrate is dumb.** The store never parses; the orchard never touches a disk except through the protocol. The same bytes land the same way in every engine, so migration is a substrate swap, not a translation.

## The protocol

In the working idiom:

```python
TABLES = ("faces", "tills", "flushes")

class Store(Protocol):
    def get(self, table: str, key: bytes) -> bytes | None: ...
    def put(self, table: str, key: bytes, value: bytes) -> None: ...
    def scan(self, table: str) -> Iterator[tuple[bytes, bytes]]:
        """every record, ascending by key bytes."""
```

Keys are the spec's byte-aligned projections (rings as big-endian u64, blooms as their 48 digest bytes); values are slurps. There is deliberately no delete and no overwrite (ruled 2026-08-01) — a store only grows, and what has grown never changes: put at a held key is a quiet no-op when the bytes are identical (retries and re-seeding are harmless) and an error when they differ. Immutability needs no parsing, so it sits below the seam; *meaning* checks (bloom-against-content, ring-tail-vs-graft-count) still belong to the orchard — the store cannot verify what bytes mean, only refuse to let them change. Wiping a prototype store is `rm -r`.

## FileStore

A directory per table; a file per record; the filename is the key's octal spelling (two digits per sip); the contents are the raw slurp bytes, identical to what any kv engine holds.

```
store/
├── faces/
│   └── <128 octal digits>       # bloom-keyed face slurps
├── tills/
│   ├── 015230603215-00000000    # found: karnak's founding second, counter 0
│   └── ...
└── flushes/
    └── 015230603215-00000006    # sow of the readme taproot
```

Octal filenames are case-free (safe on case-insensitive filesystems), shell-safe, and sort identically to the key bytes — `ls tills/` prints the log in order. `cat` shows honest binary; the human view is `hwatu inspect`, the one place glyph strings render.

## SqliteStore

A single file via stdlib `sqlite3`, one table per orchard table:

```sql
CREATE TABLE {table} (key BLOB PRIMARY KEY, value BLOB) WITHOUT ROWID;
```

**Kv discipline**: primary-key blobs, insert / point-select / ordered-scan, and nothing else — no indices, no SQL-isms — because redb is the destination and this engine exists to practice that style with zero dependencies. The b-tree's native key order is the scan order, exactly as redb's will be.

## Parametric tests

One suite runs against both engines: protocol conformance (get/put/scan round-trips, scan order, absence) and engine equivalence (the same puts produce byte-identical scans). Equivalence is the proof that no semantics leaked below the seam.

## Seeding and the golden store

Seeding is writing the genesis log ([spec deltas.md](../../spec/deltas.md)) through the store: the karnak constellation — eight records, counters 0–7 at the founding second 1784874637, and ten faces (the six mary frances schemas, till and flush, the readme's taproot and passage; ~1.7 KB in all).

Seeding is byte-reproducible — fixed founding second, deterministic blooms — so the FileStore form of a fresh seed is checked into the corpus repo as **the golden store**, `corpus/hexdown/karnak/`:

- hwatu's regression: `seed(store)` equals the golden store byte for byte
- hanafuda's acceptance: open the directory, replay, print the readme
- the seam ruling's destination grown to full size: the sealed schema slurps land in the corpus as cross-implementation fixtures, now with the whole orchard around them

## Opening

`orchard.open(store)` = read + parse + replay: scan `tills` and `flushes`, resolve each record's schema from `faces` by bloom (dynamic loading, no hardcoded constants), merge by stamp ring, dispatch by kind name, distill the projections. `just run` opens the store on disk and prints the readme.

## CLI

- `hwatu inspect <table> <key>` — one record, three ways: the glyph stream, the octal sips, and the schema-aware tree (rings as `(trunk, step)` pairs, names as words, the record's schema resolved from the store's own faces table by bloom; schema cards summarize under the metaschema). The inspector is the canonical human rendering; the stored bytes are the truth.
- `hwatu list [--plot <name>]` — plots and their documents, from the projections of an opened store.

Both commands take `--store <path>` (default `./store`) and sniff the engine from the path: a directory is a FileStore, a file is a SqliteStore. The `hwatu` command itself is a `[project.scripts]` entry point — `.venv/bin/hwatu` after an editable install.

## Migration to a key-value substrate

Open one sub-database per table; the key bytes are the kv keys; the slurp bytes are the kv values. Nothing else — no envelope to drop, no encoding to translate. Plot organization survives untouched: it lives in the log, not the storage layer.

## Open questions

- ~~Write atomicity and transaction grain~~ — ruled 2026-08-01 (philetus): hold off until the next iteration. Phase 2 does the simplest thing (plain writes, autocommit); transactions and atomicity are a stated future goal, not a current requirement.
- Whether oversized-value rejection ever relaxes toward chunking if real corpora produce oversized cards (spec stance: reject; the arbor fragments upstream).
