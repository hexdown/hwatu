"""schemas as data: the metaschema hardcoded, every other schema loaded.

a schema is the semantic dictionary for one card kind's faces: named
kinds, their admissions, crowns, and per-blossom layouts. schemas are
themselves cards -- to_face and from_face move between the dataclass
and the metaschema-shaped tree, so schema cards round-trip like any
card. hwatu ships no content vocabulary: schemas are data.

a kind's family is explicit in its spec shape (2026-07-20, superseding
one day of derived bough-ness): kids => stem, grafts => bough, layout
=> blossom, bloom-ref => position kind. values are positional
(spec/glyphs.md): stems ascend from 0o01, boughs descend from 0o57,
blossoms and position kinds descend from 0o73; reserved kinds keep
fixed values; a pad in a declaration slot skips the seat of the
declaration that follows it.

validation is loud where inference used to be silent: grafts must
name position kinds; kids must not.
"""

from dataclasses import dataclass
from typing import Union

from hwatu import layouts
from hwatu import sips
from hwatu.codec import encode_face, parse_face
from hwatu.nodes import Blossom, Face, Node, Pad, Stem

# the metaschema's own kind values -- fixed forever, known by heart
TRELLIS = 0o01
KIND = 0o02
KIDS = 0o73
CROWNS = 0o72
LAYOUT = 0o71
GRAFTS = 0o70

# reserved kinds are nameable in any kids list
RESERVED = {
    "schema": sips.SCHEMA,
    "neem": sips.NEEM,
    "graft": sips.GRAFT,
    "bloom": sips.BLOOM,
    "pad": sips.NULL,
}

NULL_HASH = (sips.BEAT,) * 64


@dataclass(frozen=True)
class Kids:
    """spec of a stem kind: names of acceptable content children."""

    names: tuple[str, ...]


@dataclass(frozen=True)
class Grafts:
    """spec of a bough kind: names of the position kinds it grafts."""

    names: tuple[str, ...]


@dataclass(frozen=True)
class Layout:
    """spec of a blossom kind: how its petals are interpreted."""

    layout: int  # layouts.PHONEME, ...


@dataclass(frozen=True)
class Ref:
    """spec of a position kind: the governing schema, by content hash.

    `target` names the schema while authoring; encoding resolves it
    through a refs mapping. parsed faces carry the 64 petals.
    """

    target: str = ""
    petals: tuple[int, ...] = ()


@dataclass(frozen=True)
class _RawKids:
    """kids as unresolved values, mid-parse only."""

    values: tuple[int, ...]


@dataclass(frozen=True)
class _RawGrafts:
    """grafts as unresolved values, mid-parse only."""

    values: tuple[int, ...]


Spec = Union[Kids, Grafts, Layout, Ref]
_AnySpec = Union[Spec, _RawKids, _RawGrafts]


@dataclass(frozen=True)
class Kind:
    name: str
    spec: _AnySpec


@dataclass(frozen=True)
class Skip:
    """a pad in a declaration slot: skips the following kind's seat."""


def _family(spec: _AnySpec) -> str:
    if isinstance(spec, (Kids, _RawKids)):
        return "stem"
    if isinstance(spec, (Grafts, _RawGrafts)):
        return "bough"
    return "blossom"  # Layout and Ref: position kinds take blossom seats


@dataclass(frozen=True)
class Schema:
    name: str
    crowns: tuple[str, ...]
    kinds: tuple[Kind | Skip, ...]

    def values(self) -> dict[str, int]:
        """name -> kind value, per the positional assignment rules."""
        out = dict(RESERVED)
        seats = {"stem": 0o01, "bough": 0o57, "blossom": 0o73}
        steps = {"stem": 1, "bough": -1, "blossom": -1}
        for i, k in enumerate(self.kinds):
            if isinstance(k, Skip):
                nxt = _next_kind(self.kinds, i)
                if nxt is not None:
                    fam = _family(nxt.spec)
                    seats[fam] += steps[fam]
                continue
            fam = _family(k.spec)
            out[k.name] = seats[fam]
            seats[fam] += steps[fam]
        self._check(out)
        return out

    def names(self) -> dict[int, str]:
        return {v: n for n, v in self.values().items()}

    def kind(self, name: str) -> Kind:
        for k in self.kinds:
            if isinstance(k, Kind) and k.name == name:
                return k
        raise KeyError(f"schema {self.name!r} declares no kind {name!r}")

    def _check(self, values: dict[str, int]) -> None:
        """grafts name position kinds; kids must not."""
        positions = {
            k.name
            for k in self.kinds
            if isinstance(k, Kind) and isinstance(k.spec, Ref)
        }
        position_values = {values[n] for n in positions}
        for k in self.kinds:
            if not isinstance(k, Kind):
                continue
            if isinstance(k.spec, Grafts):
                stray = set(k.spec.names) - positions
                if stray:
                    raise ValueError(
                        f"bough {k.name!r} grafts non-position "
                        f"kinds: {sorted(stray)}"
                    )
            elif isinstance(k.spec, _RawGrafts):
                if set(k.spec.values) - position_values:
                    raise ValueError(
                        f"bough {k.name!r} grafts non-position kinds"
                    )
            elif isinstance(k.spec, Kids):
                caught = set(k.spec.names) & positions
                if caught:
                    raise ValueError(
                        f"stem {k.name!r} admits position "
                        f"kinds: {sorted(caught)}"
                    )
            elif isinstance(k.spec, _RawKids):
                if set(k.spec.values) & position_values:
                    raise ValueError(f"stem {k.name!r} admits position kinds")


def _next_kind(kinds: tuple[Kind | Skip, ...], i: int) -> Kind | None:
    for later in kinds[i + 1 :]:
        if isinstance(later, Kind):
            return later
    return None


def _name(text: str) -> Blossom:
    return Blossom(sips.NEEM, layouts.word(text))


def to_face(
    schema: Schema, refs: dict[str, tuple[int, ...]] | None = None
) -> Face:
    """the schema as a card face: null-hash schema node, trellis root.

    `refs` maps position-kind targets to their 64 hash petals; leaf
    schemas need none.
    """
    values = schema.values()
    decls: list[Node] = []
    for k in schema.kinds:
        if isinstance(k, Skip):
            decls.append(Pad())
            continue
        spec = k.spec
        if isinstance(spec, (_RawKids, _RawGrafts)):
            raise ValueError("resolve kids to names before encoding")
        if isinstance(spec, (Kids, Grafts)):
            petals = tuple(values[n] for n in spec.names)
            body: Node = Blossom(
                KIDS if isinstance(spec, Kids) else GRAFTS, petals
            )
        elif isinstance(spec, Layout):
            body = Blossom(LAYOUT, (spec.layout,))
        else:
            hash_ = spec.petals or (refs or {}).get(spec.target, ())
            if len(hash_) != 64:
                raise ValueError(
                    f"position kind {k.name!r} needs 64 hash petals"
                )
            body = Blossom(sips.BLOOM, hash_)
        decls.append(Stem(KIND, (_name(k.name), body)))
    root = Stem(
        TRELLIS,
        (
            _name(schema.name),
            Blossom(CROWNS, tuple(values[n] for n in schema.crowns)),
            *decls,
        ),
    )
    bloom = Blossom(sips.BLOOM, NULL_HASH)
    return Face(0, Stem(sips.SCHEMA, (bloom, root)), 0)


def from_face(face: Face) -> Schema:
    """read a schema card's face back into a Schema."""
    bloom, root = face.root.kids
    if not (isinstance(bloom, Blossom) and bloom.petals == NULL_HASH):
        raise ValueError("schema cards carry the null hash")
    if not (isinstance(root, Stem) and root.kind == TRELLIS):
        raise ValueError("a schema card's root is a trellis")
    name_node, crowns_node, *decls = root.kids
    kinds: list[Kind | Skip] = []
    for d in decls:
        if isinstance(d, Pad):
            kinds.append(Skip())
            continue
        if not (isinstance(d, Stem) and d.kind == KIND):
            raise ValueError("schema declarations are kind nodes")
        kname = layouts.text(_petals(d.kids[0]))
        kinds.append(Kind(kname, _spec_of(d.kids[1])))
    draft = Schema("", (), tuple(kinds))
    names = draft.names()

    def resolve(k: Kind | Skip) -> Kind | Skip:
        if isinstance(k, Kind) and isinstance(k.spec, _RawKids):
            return Kind(k.name, Kids(tuple(names[v] for v in k.spec.values)))
        if isinstance(k, Kind) and isinstance(k.spec, _RawGrafts):
            return Kind(k.name, Grafts(tuple(names[v] for v in k.spec.values)))
        return k

    crowns = tuple(names[v] for v in _petals(crowns_node))
    return Schema(
        layouts.text(_petals(name_node)),
        crowns,
        tuple(resolve(k) for k in kinds),
    )


def _spec_of(node: Node) -> _AnySpec:
    if not isinstance(node, Blossom):
        raise ValueError("a kind's spec is a blossom")
    if node.kind == KIDS:
        return _RawKids(node.petals)
    if node.kind == GRAFTS:
        return _RawGrafts(node.petals)
    if node.kind == LAYOUT:
        return Layout(node.petals[0])
    if node.kind == sips.BLOOM:
        return Ref(petals=node.petals)
    raise ValueError(f"unknown spec kind {node.kind:#o}")


def _petals(node: Node) -> tuple[int, ...]:
    if not isinstance(node, Blossom):
        raise ValueError("expected a blossom")
    return node.petals


def sips_of(
    schema: Schema, refs: dict[str, tuple[int, ...]] | None = None
) -> tuple[int, ...]:
    """the schema card's full sip stream."""
    return encode_face(to_face(schema, refs))


def load(stream: tuple[int, ...]) -> Schema:
    """a schema from its sip stream."""
    return from_face(parse_face(stream))


def chain(schemas: dict[str, Schema]) -> dict[str, bytes]:
    """seal a dependency-ordered schema set to canonical slurp bytes.

    every Ref target must precede its referrer; each schema's bloom
    feeds the refs of those that follow. the generic mechanism behind
    seeding any orchard -- the schema *data* lives with its corpus,
    never in this library.
    """
    from hwatu import slurp

    blooms: dict[str, tuple[int, ...]] = {}
    out: dict[str, bytes] = {}
    for name, schema in schemas.items():
        data = slurp.seal(sips_of(schema, refs=blooms))
        blooms[name] = slurp.bloom_of(data)
        out[name] = data
    return out
