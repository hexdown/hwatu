"""the cli: inspect shows a record three ways, list walks the plots.

driven as plain function calls -- main(argv) with an injected store
path -- no subprocess required.
"""

from pathlib import Path

import genesis
import pytest

from hwatu import cli, slurp, store

FOUND_NAME = "015230603215-00000000"
SOW_NAME = "015230603215-00000006"


@pytest.fixture()
def ground(tmp_path: Path) -> str:
    path = tmp_path / "karnak"
    genesis.seed(store.FileStore(path))
    return str(path)


def _bloom_name(data: bytes) -> str:
    return store.spell(store.bloom_key(slurp.bloom_of(data)))


def test_inspect_shows_a_till_three_ways(ground: str, capsys):
    assert cli.main(["inspect", "tills", FOUND_NAME, "--store", ground]) == 0
    out = capsys.readouterr().out
    assert f"tills/{FOUND_NAME}" in out
    assert "glyphs:" in out
    assert "octal:" in out
    assert "a record under till:" in out
    assert "found" in out
    assert "neem ‹karnak›" in out


def test_inspect_decodes_rings_in_a_sow(ground: str, capsys):
    assert cli.main(["inspect", "flushes", SOW_NAME, "--store", ground]) == 0
    out = capsys.readouterr().out
    assert "a record under flush:" in out
    assert "sow" in out
    assert "ring ‹(0, 0)›" in out  # the taproot's stead ring
    assert "ring ‹(0, 4)›" in out  # the prose plot ring
    assert "ring ‹(0, 6)›" in out  # the graft tail: the readme leaf


def test_inspect_shows_a_face_under_its_schema(ground: str, capsys):
    name = _bloom_name(genesis.faces()["readme-passage"])
    assert cli.main(["inspect", "faces", name, "--store", ground]) == 0
    out = capsys.readouterr().out
    assert "a face under passage:" in out
    assert "neem ‹welcome›" in out


def test_inspect_summarizes_a_schema_card(ground: str, capsys):
    name = _bloom_name(genesis.faces()["passage"])
    assert cli.main(["inspect", "faces", name, "--store", ground]) == 0
    out = capsys.readouterr().out
    assert "a schema card, parsed under the metaschema: passage" in out
    assert "statement" in out


def test_inspect_of_an_absent_record_fails_cleanly(ground: str, capsys):
    missing = "015230603215-00000077"
    code = cli.main(["inspect", "tills", missing, "--store", ground])
    assert code == 1
    assert "no record" in capsys.readouterr().err


def test_list_walks_the_plots(ground: str, capsys):
    assert cli.main(["list", "--store", ground]) == 0
    out = capsys.readouterr().out
    assert "the karnak orchard — 4 plots, 1 document" in out
    for plot in ("plots", "schemas", "gardeners", "prose"):
        assert plot in out
    assert "(0, 0) — 2 cards" in out


def test_list_filters_to_one_plot(ground: str, capsys):
    assert cli.main(["list", "--plot", "prose", "--store", ground]) == 0
    out = capsys.readouterr().out
    assert "prose" in out
    assert "gardeners" not in out


def test_an_unknown_plot_fails_cleanly(ground: str, capsys):
    assert cli.main(["list", "--plot", "weeds", "--store", ground]) == 1
    assert "no plot" in capsys.readouterr().err


def test_the_sqlite_engine_serves_the_cli(tmp_path: Path, capsys):
    path = tmp_path / "karnak.db"
    genesis.seed(store.SqliteStore(path))
    assert cli.main(["list", "--store", str(path)]) == 0
    assert "karnak" in capsys.readouterr().out


def test_a_missing_store_fails_cleanly(tmp_path: Path, capsys):
    code = cli.main(["list", "--store", str(tmp_path / "nowhere")])
    assert code == 1
    assert "no store" in capsys.readouterr().err
