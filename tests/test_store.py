"""the store protocol and its two engines, held to one contract.

keys are byte projections -- rings big-endian in a word, blooms
their own digests -- names are octal sip spellings, values are
opaque bytes. the parametric suite proves the engines
interchangeable; the equivalence test proves no semantics leaked
below the seam.
"""

import hashlib
from pathlib import Path

import pytest

from hwatu import slurp, store
from hwatu.store import Store

RING = (1784874637, 0)
RING_KEY = store.ring_key(RING)
RING_NAME = "015230603215-00000000"


# projections


def test_a_ring_key_is_its_big_endian_word():
    assert RING_KEY == (1784874637 << 24).to_bytes(8, "big")
    assert store.key_ring(RING_KEY) == RING


def test_ring_byte_order_is_ring_order():
    rings = [(0, 0), (0, 1), (1, 0), (1784874637, 7), (2**36 - 1, 0)]
    keys = [store.ring_key(ring) for ring in rings]
    assert sorted(keys) == keys
    assert [store.key_ring(key) for key in keys] == rings


def test_a_ring_key_refuses_more_than_its_bits():
    with pytest.raises(ValueError):
        store.ring_key((1 << 36, 0))
    with pytest.raises(ValueError):
        store.ring_key((0, 1 << 24))


def test_a_blooms_byte_projection_is_its_digest():
    data = b"the rooster speaks"
    digest = hashlib.blake2b(data, digest_size=48).digest()
    assert store.bloom_key(slurp.bloom_of(data)) == digest
    assert store.key_bloom(digest) == slurp.bloom_of(data)


# spelling


def test_a_ring_spells_octal_with_a_hyphen():
    assert store.spell(RING_KEY) == RING_NAME
    assert store.unspell(RING_NAME) == RING_KEY


def test_a_bloom_spells_128_unbroken_digits():
    key = store.bloom_key(tuple(range(64)))
    name = store.spell(key)
    assert len(name) == 128
    assert name.startswith("0001020304050607")
    assert name[16:18] == "10"  # petal eight, in octal
    assert store.unspell(name) == key


def test_spelled_names_sort_like_key_bytes():
    rings = [(0, 5), (7, 2**24 - 1), (1784874637, 0), (2**35, 3)]
    keys = sorted(store.ring_key(ring) for ring in rings)
    names = sorted(store.spell(key) for key in keys)
    assert [store.unspell(name) for name in names] == keys


def test_a_malformed_name_is_refused():
    with pytest.raises(ValueError):
        store.unspell("015230603215-000")
    with pytest.raises(ValueError):
        store.unspell("0102")


# the engines, held to the protocol


@pytest.fixture(params=["file", "sqlite"])
def backing(request: pytest.FixtureRequest, tmp_path: Path) -> Store:
    if request.param == "file":
        return store.FileStore(tmp_path / "ground")
    return store.SqliteStore(tmp_path / "ground.db")


def test_a_fresh_store_is_empty(backing: Store):
    for table in store.TABLES:
        assert list(backing.scan(table)) == []


def test_get_returns_what_put_stored(backing: Store):
    backing.put("tills", RING_KEY, b"first light")
    assert backing.get("tills", RING_KEY) == b"first light"


def test_an_absent_key_reads_none(backing: Store):
    assert backing.get("faces", store.bloom_key(tuple(range(64)))) is None


def test_put_never_changes_what_a_key_holds(backing: Store):
    backing.put("tills", RING_KEY, b"first")
    with pytest.raises(ValueError):
        backing.put("tills", RING_KEY, b"second")
    assert backing.get("tills", RING_KEY) == b"first"


def test_an_identical_reput_is_a_quiet_nothing(backing: Store):
    backing.put("tills", RING_KEY, b"same")
    backing.put("tills", RING_KEY, b"same")
    assert backing.get("tills", RING_KEY) == b"same"


def test_scan_walks_ascending_key_bytes(backing: Store):
    late = store.ring_key((1784874637, 7))
    early = store.ring_key((1784874637, 0))
    backing.put("flushes", late, b"late")
    backing.put("flushes", early, b"early")
    assert list(backing.scan("flushes")) == [
        (early, b"early"),
        (late, b"late"),
    ]


def test_each_table_keeps_its_own_key_space(backing: Store):
    backing.put("tills", RING_KEY, b"till")
    backing.put("flushes", RING_KEY, b"flush")
    assert backing.get("tills", RING_KEY) == b"till"
    assert backing.get("flushes", RING_KEY) == b"flush"


def test_an_unknown_table_is_refused(backing: Store):
    with pytest.raises(ValueError):
        backing.put("weeds", RING_KEY, b"no")
    with pytest.raises(ValueError):
        backing.get("weeds", RING_KEY)
    with pytest.raises(ValueError):
        list(backing.scan("weeds"))


def test_the_engines_agree_byte_for_byte(tmp_path: Path):
    filestore = store.FileStore(tmp_path / "ground")
    sqlitestore = store.SqliteStore(tmp_path / "ground.db")
    records = [
        ("tills", store.ring_key((1784874637, 0)), b"found"),
        ("faces", store.bloom_key(tuple(range(64))), b"petals"),
        ("flushes", store.ring_key((1784874637, 6)), b"sow"),
    ]
    for table, key, value in records:
        filestore.put(table, key, value)
        sqlitestore.put(table, key, value)
    for table in store.TABLES:
        assert list(filestore.scan(table)) == list(sqlitestore.scan(table))


def test_the_filestore_is_honest_bytes(tmp_path: Path):
    ground = tmp_path / "ground"
    backing = store.FileStore(ground)
    backing.put("tills", RING_KEY, b"cat me")
    record = ground / "tills" / RING_NAME
    assert record.read_bytes() == b"cat me"
