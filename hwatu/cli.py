"""the hwatu cli: inspect records and list an orchard's plots.

the inspector is the one place glyph strings render -- the stored
bytes stay honest binary, and the human views live here, above the
protocol. `hwatu inspect` shows one record three ways: the glyph
stream, the octal sips, and the schema-aware tree, with the record's
schema resolved from the store's own faces table by bloom. `hwatu
list` opens the orchard and walks its projections. both take
`--store` and sniff the engine from the path: a directory is a
FileStore, a file is a SqliteStore. per hwatu/design/store.md.
"""

import argparse
import sys
from collections.abc import Mapping
from pathlib import Path

from hwatu import layouts, orchard, schema, sips, slurp, store
from hwatu.codec import parse_face
from hwatu.nodes import Blossom, Node, Pad
from hwatu.schema import Kind, Layout, Schema


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hwatu", description="tend a hexdown orchard from the shell"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--store",
        default="store",
        help="a filestore directory or a sqlite file (default: ./store)",
    )
    inspect_parser = commands.add_parser(
        "inspect",
        parents=[shared],
        help="one record, three ways: glyphs, octal, the decoded tree",
    )
    inspect_parser.add_argument("table", choices=store.TABLES)
    inspect_parser.add_argument(
        "key", help="the record's octal name (its filename)"
    )
    inspect_parser.set_defaults(run=_inspect)
    list_parser = commands.add_parser(
        "list", parents=[shared], help="plots and their documents"
    )
    list_parser.add_argument("--plot", help="show only this plot")
    list_parser.set_defaults(run=_list)
    arguments = parser.parse_args(argv)
    try:
        return arguments.run(arguments)
    except ValueError as error:
        print(f"hwatu: {error}", file=sys.stderr)
        return 1


def _backing(path_text: str) -> store.Store:
    """sniff the engine: a directory of tables or a sqlite file."""
    path = Path(path_text)
    if path.is_dir():
        if all((path / table).is_dir() for table in store.TABLES):
            return store.FileStore(path)
        raise ValueError(f"{path} is not a filestore: table dirs missing")
    if path.is_file():
        return store.SqliteStore(path)
    raise ValueError(f"no store at {path}")


# inspect: one record, three ways


def _inspect(arguments: argparse.Namespace) -> int:
    backing = _backing(arguments.store)
    key = store.unspell(arguments.key)
    data = backing.get(arguments.table, key)
    if data is None:
        print(
            f"hwatu: no record {arguments.table}/{arguments.key}",
            file=sys.stderr,
        )
        return 1
    face_sips = slurp.unpack(data)
    face = parse_face(face_sips)
    print(f"{arguments.table}/{arguments.key}")
    print(
        f"{len(data)} bytes; {len(face_sips)} sips "
        f"({face.lead} lead, {face.tail} tail)"
    )
    print()
    print("glyphs:")
    for row in _rows(face_sips):
        print("  " + sips.glyphs(row))
    print("octal:")
    for row in _rows(face_sips):
        print("  " + "".join(f"{value:02o}" for value in row))
    print()
    governor = face.root.kids[0]
    if not isinstance(governor, Blossom):
        raise ValueError("a face opens with its schema bloom")
    if governor.petals == schema.NULL_HASH:
        _summarize_schema(schema.load(face_sips))
        return 0
    schema_data = backing.get("faces", store.bloom_key(governor.petals))
    if schema_data is None:
        print("schema not at hand; the bare tree:")
        _print_tree(face.root.kids[1], {}, {})
        return 0
    speaks = schema.load(slurp.unpack(schema_data))
    body = "record" if arguments.table in ("tills", "flushes") else "face"
    print(f"a {body} under {speaks.name}:")
    names, specs = _vocabulary(speaks)
    _print_tree(face.root.kids[1], names, specs)
    return 0


def _rows(values: tuple[int, ...]) -> list[tuple[int, ...]]:
    """one 24-byte increment of 32 sips per display row."""
    return [values[start : start + 32] for start in range(0, len(values), 32)]


def _summarize_schema(speaks: Schema) -> None:
    kinds = ", ".join(
        kind.name for kind in speaks.kinds if isinstance(kind, Kind)
    )
    print(f"a schema card, parsed under the metaschema: {speaks.name}")
    print(f"  crowns: {', '.join(speaks.crowns)}")
    print(f"  kinds: {kinds}")


def _vocabulary(
    speaks: Schema,
) -> tuple[dict[int, str], Mapping[int, object]]:
    values = speaks.values()
    specs = {
        values[kind.name]: kind.spec
        for kind in speaks.kinds
        if isinstance(kind, Kind)
    }
    return speaks.names(), specs


def _print_tree(
    node: Node, names: dict[int, str], specs: Mapping[int, object]
) -> None:
    lines: list[str] = []
    _describe(node, names, specs, 1, lines)
    print("\n".join(lines))


def _describe(
    node: Node,
    names: dict[int, str],
    specs: Mapping[int, object],
    depth: int,
    lines: list[str],
) -> None:
    indent = "  " * depth
    if isinstance(node, Pad):
        lines.append(indent + "pad")
        return
    if isinstance(node, Blossom):
        lines.append(indent + _blossom_line(node, names, specs))
        return
    lines.append(indent + _label(node.kind, names))
    for kid in node.kids:
        _describe(kid, names, specs, depth + 1, lines)


def _label(kind: int, names: dict[int, str]) -> str:
    return names.get(kind, f"{kind:#o}")


def _blossom_line(
    node: Blossom, names: dict[int, str], specs: Mapping[int, object]
) -> str:
    if node.kind == sips.NEEM:
        return f"neem ‹{layouts.text(node.petals)}›"
    if node.kind == sips.GRAFT:
        return f"graft ‹{_label(node.petals[0], names)}›"
    if node.kind == sips.BLOOM:
        if node.petals == schema.NULL_HASH:
            return "bloom ‹null›"
        name = store.spell(store.bloom_key(node.petals))
        return f"bloom ‹{name[:12]}…›"
    label = _label(node.kind, names)
    spec = specs.get(node.kind)
    if isinstance(spec, Layout):
        decoded = layouts.LAYOUTS[spec.layout][1](node.petals)
        return f"{label} ‹{decoded}›"
    petals = " ".join(f"{petal:02o}" for petal in node.petals)
    return f"{label} ‹{petals}›"


# list: plots and their documents, from the projections


def _list(arguments: argparse.Namespace) -> int:
    backing = _backing(arguments.store)
    grove = orchard.open(backing)
    if arguments.plot is not None and (
        arguments.plot not in grove.plots.values()
    ):
        print(f"hwatu: no plot {arguments.plot!r}", file=sys.stderr)
        return 1
    print(
        f"the {grove.name} orchard — {_count(len(grove.plots), 'plot')}, "
        f"{_count(len(grove.documents), 'document')}"
    )
    for plot_ring, plot_name in grove.plots.items():
        if arguments.plot is not None and plot_name != arguments.plot:
            continue
        taproots = [
            taproot
            for taproot, plot in grove.documents.items()
            if plot == plot_ring
        ]
        trunk, step = plot_ring
        held = _count(len(taproots), "document") if taproots else "empty"
        print(f"{plot_name} ({trunk}, {step}): {held}")
        for taproot in taproots:
            cards = sum(1 for ring in grove.backs if ring[0] == taproot[0])
            print(f"  ({taproot[0]}, {taproot[1]}) — {_count(cards, 'card')}")
    return 0


def _count(number: int, word: str) -> str:
    return f"{number} {word}" + ("" if number == 1 else "s")


if __name__ == "__main__":
    raise SystemExit(main())
