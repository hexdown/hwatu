"""the store: three tables of bytes under sorted byte keys.

level 0 of the two-level architecture (spec/store.md): the store
never parses; the orchard never touches a disk except through the
protocol. keys are the spec's byte-aligned projections -- rings as
their 60 bits big-endian in a word, blooms as their own blake2b-384
digests -- and where an engine names records as files, keys spell in
octal, two digits per sip. values are opaque slurp bytes. there is
no delete and no overwrite: a store only grows, and what has grown
never changes -- put refuses to alter a held key (an identical
re-put is a quiet no-op, so retries and re-seeding are harmless).
discarding a store is a substrate operation, not a protocol verb.

two engines ship: FileStore (a directory per table, a file per
record, cat-able honest bytes) and SqliteStore (stdlib sqlite3 under
kv discipline -- primary-key blobs, point reads, ordered scans,
nothing else -- because redb is the destination). one parametric
suite holds both to the contract.
"""

import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from hwatu import slurp
from hwatu.layouts import Ring

TABLES = ("faces", "tills", "flushes")


# the byte-aligned projections (spec/data-model.md): sips are the
# authoritative representation; these bytes are how rings and blooms
# serve as kv keys, chosen so byte order equals meaning


def ring_key(ring: Ring) -> bytes:
    """a ring's byte projection: its 60 bits big-endian in a word."""
    high, low = ring
    if not 0 <= high < 1 << 36:
        raise ValueError(f"a ring's high half holds 36 bits; got {high}")
    if not 0 <= low < 1 << 24:
        raise ValueError(f"a ring's low half holds 24 bits; got {low}")
    return ((high << 24) | low).to_bytes(8, "big")


def key_ring(key: bytes) -> Ring:
    """the ring a key projects: (trunk, step) or (stamp, counter)."""
    if len(key) != 8:
        raise ValueError(f"a ring key is eight bytes; got {len(key)}")
    value = int.from_bytes(key, "big")
    if value >> 60:
        raise ValueError("a ring key's four lead bits are zero")
    return (value >> 24, value & ((1 << 24) - 1))


def bloom_key(petals: tuple[int, ...]) -> bytes:
    """a bloom's byte projection: exactly its blake2b-384 digest."""
    if len(petals) != 64:
        raise ValueError(f"a bloom carries 64 petals; got {len(petals)}")
    return slurp.pack(petals)


def key_bloom(key: bytes) -> tuple[int, ...]:
    """the 64 petals a bloom key packs."""
    if len(key) != 48:
        raise ValueError(f"a bloom key is 48 digest bytes; got {len(key)}")
    return slurp.unpack(key)


# the octal spelling (spec/data-model.md): projections are for keys,
# names are for sips -- two octal digits per sip keeps every sip
# boundary visible, survives case-insensitive filesystems, and sorts
# identically to the key bytes


def spell(key: bytes) -> str:
    """a key's octal name: two digits per sip, ring halves hyphenated."""
    if len(key) == 8:
        high, low = key_ring(key)
        return f"{high:012o}-{low:08o}"
    if len(key) == 48:
        return "".join(f"{petal:02o}" for petal in key_bloom(key))
    raise ValueError(f"a key is 8 ring or 48 bloom bytes; got {len(key)}")


def unspell(name: str) -> bytes:
    """the key an octal name spells."""
    if "-" in name:
        high_text, _, low_text = name.partition("-")
        if len(high_text) != 12 or len(low_text) != 8:
            raise ValueError(
                f"a ring name is twelve digits, a hyphen, eight: {name!r}"
            )
        return ring_key((int(high_text, 8), int(low_text, 8)))
    if len(name) != 128:
        raise ValueError(f"a bloom name is 128 octal digits: {name!r}")
    petals = tuple(int(name[i : i + 2], 8) for i in range(0, 128, 2))
    return bloom_key(petals)


class Store(Protocol):
    """the level-0 contract: get, put, sorted scan -- no delete, and
    put never changes what a held key holds."""

    def get(self, table: str, key: bytes) -> bytes | None: ...

    def put(self, table: str, key: bytes, value: bytes) -> None: ...

    def scan(self, table: str) -> Iterator[tuple[bytes, bytes]]: ...


def _known(table: str) -> str:
    if table not in TABLES:
        raise ValueError(f"no table {table!r}; the tables are {TABLES}")
    return table


class FileStore:
    """a directory per table, a file per record.

    the filename is the key's octal spelling, the contents are the
    raw value bytes -- identical to what any kv engine holds, so a
    directory listing of a log is the log in order and `cat` shows
    honest binary. writes are plain (atomicity deferred, ruled
    2026-08-01).
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        for table in TABLES:
            (self.root / table).mkdir(parents=True, exist_ok=True)

    def get(self, table: str, key: bytes) -> bytes | None:
        record = self.root / _known(table) / spell(key)
        return record.read_bytes() if record.exists() else None

    def put(self, table: str, key: bytes, value: bytes) -> None:
        record = self.root / _known(table) / spell(key)
        if record.exists():
            if record.read_bytes() == value:
                return
            raise ValueError(f"a store never overwrites: {table}/{record.name}")
        record.write_bytes(value)

    def scan(self, table: str) -> Iterator[tuple[bytes, bytes]]:
        directory = self.root / _known(table)
        return (
            (unspell(record.name), record.read_bytes())
            for record in sorted(directory.iterdir())
        )


class SqliteStore:
    """a single sqlite file, one (key, value) table per orchard table.

    kv discipline: primary-key blobs, insert, point-select, ordered
    scan, and nothing else -- no indices, no sql-isms -- because redb
    is the destination and this engine exists to practice that style
    with zero dependencies. autocommit (atomicity deferred, ruled
    2026-08-01); the b-tree's native key order is the scan order.
    """

    def __init__(self, path: Path | str) -> None:
        self.connection = sqlite3.connect(path, autocommit=True)
        for table in TABLES:
            self.connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table} "
                "(key BLOB PRIMARY KEY, value BLOB) WITHOUT ROWID"
            )

    def get(self, table: str, key: bytes) -> bytes | None:
        row = self.connection.execute(
            f"SELECT value FROM {_known(table)} WHERE key = ?", (key,)
        ).fetchone()
        return None if row is None else row[0]

    def put(self, table: str, key: bytes, value: bytes) -> None:
        held = self.get(table, key)
        if held is not None:
            if held == value:
                return
            raise ValueError(f"a store never overwrites: {table}/{spell(key)}")
        self.connection.execute(
            f"INSERT INTO {_known(table)} VALUES (?, ?)", (key, value)
        )

    def scan(self, table: str) -> Iterator[tuple[bytes, bytes]]:
        rows = self.connection.execute(
            f"SELECT key, value FROM {_known(table)} ORDER BY key"
        )
        return ((key, value) for key, value in rows)
