"""semantic validation: per-subtree verdicts for a tree under a schema.

structure is public grammar -- parsing never fails on complete streams
-- so fit to a schema is judged after the fact, tree-sitter style:
validate walks a parsed tree with the schema as its dictionary and
returns a verdict for every spot where the face strays, an empty tuple
meaning the face validates. verdicts localize: a stray subtree never
silences its siblings, and judgment continues beneath the stray.

positional seats keep each family's kind values in the family's own
range, so family agreement needs no checking; verdicts speak
vocabulary and shape. the rules, per spec/encoding.md:

- crown: the card root's kind must be one the schema crowns
- admission: a stem's children must be kinds its kids list names
- family: a bough's children must all be grafts
- graft: a graft's petal must name a grafted position kind
- arity: grafts carry exactly one petal, blooms exactly 64
- face: the schema node holds a bloom and the card root, in order
- unknown: kinds the schema never declares, reported where no
  admission rule reaches them
"""

from dataclasses import dataclass

from hwatu import sips
from hwatu.nodes import Blossom, Bough, Face, Node, Pad, Stem
from hwatu.schema import Grafts, Kids, Kind, Ref, Schema


@dataclass(frozen=True)
class Verdict:
    """one localized complaint; the path is child indices from the
    walked root (in a face, (0,) is the bloom, (1,) the card root)."""

    path: tuple[int, ...]
    rule: str
    report: str


@dataclass(frozen=True)
class _Lexicon:
    """the schema's dictionary, resolved to kind values for the walk."""

    names: dict[int, str]
    crowns: frozenset[int]
    admits: dict[int, frozenset[int]]  # stem kind -> admitted child kinds
    grafts: dict[int, frozenset[int]]  # bough kind -> admitted graft petals
    positions: frozenset[int]  # every grafted position kind


def validate(
    node: Node, schema: Schema, at: tuple[int, ...] = ()
) -> tuple[Verdict, ...]:
    """judge one subtree; the node's own kind is its parent's business
    (or the crown rule's, at a card root -- see validate_face)."""
    out: list[Verdict] = []
    _walk(node, at, _lexicon(schema), out)
    return tuple(out)


def validate_face(face: Face, schema: Schema) -> tuple[Verdict, ...]:
    """judge a whole face: the schema-node silhouette, the crown, and
    the tree beneath."""
    out: list[Verdict] = []
    lexicon = _lexicon(schema)
    root = face.root
    if root.kind != sips.SCHEMA:
        out.append(
            Verdict(
                (),
                "face",
                f"a face opens with the schema node; found {root.kind:#o}",
            )
        )
    if len(root.kids) != 2:
        out.append(
            Verdict(
                (),
                "face",
                "a schema node holds a bloom and the card root; "
                f"found {len(root.kids)} children",
            )
        )
        return tuple(out)
    bloom, crown = root.kids
    if not (isinstance(bloom, Blossom) and bloom.kind == sips.BLOOM):
        out.append(
            Verdict((0,), "face", "a schema node's first child is its bloom")
        )
    elif len(bloom.petals) != 64:
        out.append(
            Verdict(
                (0,),
                "arity",
                f"a bloom carries 64 petals; found {len(bloom.petals)}",
            )
        )
    if isinstance(crown, Pad):
        out.append(Verdict((1,), "crown", "the card root is a pad"))
        return tuple(out)
    if crown.kind not in lexicon.crowns:
        out.append(
            Verdict(
                (1,),
                "crown",
                f"{_spoken(crown.kind, lexicon)} is not a crown "
                f"of {schema.name!r}",
            )
        )
    _walk(crown, (1,), lexicon, out)
    return tuple(out)


def _lexicon(schema: Schema) -> _Lexicon:
    values = schema.values()
    admits: dict[int, frozenset[int]] = {}
    grafts: dict[int, frozenset[int]] = {}
    for k in schema.kinds:
        if not isinstance(k, Kind):
            continue
        if isinstance(k.spec, Kids):
            admits[values[k.name]] = frozenset(
                values[name] for name in k.spec.names
            )
        elif isinstance(k.spec, Grafts):
            grafts[values[k.name]] = frozenset(
                values[name] for name in k.spec.names
            )
    positions = frozenset(
        values[k.name]
        for k in schema.kinds
        if isinstance(k, Kind) and isinstance(k.spec, Ref)
    )
    crowns = frozenset(values[name] for name in schema.crowns)
    return _Lexicon(schema.names(), crowns, admits, grafts, positions)


def _spoken(kind: int, lexicon: _Lexicon) -> str:
    name = lexicon.names.get(kind)
    return f"kind {name!r}" if name else f"kind {kind:#o}"


def _walk(
    node: Node, path: tuple[int, ...], lexicon: _Lexicon, out: list[Verdict]
) -> None:
    if isinstance(node, Pad):
        return
    if isinstance(node, Blossom):
        _blossom(node, path, lexicon, out)
        return
    if isinstance(node, Bough):
        _bough(node, path, lexicon, out)
        return
    _stem(node, path, lexicon, out)


def _blossom(
    node: Blossom, path: tuple[int, ...], lexicon: _Lexicon, out: list[Verdict]
) -> None:
    """the reserved shapes hold in every context."""
    if node.kind == sips.GRAFT:
        if len(node.petals) != 1:
            out.append(
                Verdict(
                    path,
                    "arity",
                    "a graft carries exactly one petal; "
                    f"found {len(node.petals)}",
                )
            )
        elif node.petals[0] not in lexicon.positions:
            out.append(
                Verdict(
                    path,
                    "graft",
                    f"petal {node.petals[0]:#o} names no grafted position kind",
                )
            )
    elif node.kind == sips.BLOOM and len(node.petals) != 64:
        out.append(
            Verdict(
                path,
                "arity",
                f"a bloom carries 64 petals; found {len(node.petals)}",
            )
        )


def _bough(
    node: Bough, path: tuple[int, ...], lexicon: _Lexicon, out: list[Verdict]
) -> None:
    """children must all be grafts, their petals in the grafted set."""
    allowed = lexicon.grafts.get(node.kind, lexicon.positions)
    for i, kid in enumerate(node.kids):
        kid_path = (*path, i)
        if isinstance(kid, Blossom) and kid.kind == sips.GRAFT:
            if len(kid.petals) != 1:
                out.append(
                    Verdict(
                        kid_path,
                        "arity",
                        "a graft carries exactly one petal; "
                        f"found {len(kid.petals)}",
                    )
                )
            elif kid.petals[0] not in allowed:
                out.append(
                    Verdict(
                        kid_path,
                        "graft",
                        f"petal {kid.petals[0]:#o} is not grafted "
                        f"by {_spoken(node.kind, lexicon)}",
                    )
                )
            continue
        found = "a pad" if isinstance(kid, Pad) else _spoken(kid.kind, lexicon)
        out.append(
            Verdict(
                kid_path,
                "family",
                f"a bough's children are all grafts; found {found}",
            )
        )
        _walk(kid, kid_path, lexicon, out)


def _stem(
    node: Stem, path: tuple[int, ...], lexicon: _Lexicon, out: list[Verdict]
) -> None:
    """children must be admitted by the kids list; pads hold absences."""
    admitted = lexicon.admits.get(node.kind)
    for i, kid in enumerate(node.kids):
        kid_path = (*path, i)
        if isinstance(kid, Pad):
            continue  # an intentionally empty slot
        if admitted is None:
            # no kids list to consult: judge the child on its own
            if kid.kind not in lexicon.names:
                out.append(
                    Verdict(
                        kid_path,
                        "unknown",
                        f"the schema declares no kind {kid.kind:#o}",
                    )
                )
        elif kid.kind not in admitted:
            out.append(
                Verdict(
                    kid_path,
                    "admission",
                    f"{_spoken(node.kind, lexicon)} does not admit "
                    f"{_spoken(kid.kind, lexicon)}",
                )
            )
        _walk(kid, kid_path, lexicon, out)
