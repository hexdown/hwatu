"""opening an orchard is replaying the log.

durable truth is faces plus deltas; everything mutable is a
projection distilled in ram by walking the tills and flushes in
stamp order (tills first on ties -- presuppositions precede
operations). the rulebook dispatches on act kind names, the renderer
pattern: unknown kinds skip gracefully, so the delta vocabulary can
grow without stranding older parsers.

the projections stay lean. a back is a face bloom plus child rings;
a card's document is the high half of its own ring, and the
document's taproot ring (document, 0) binds the plot -- membership
is arithmetic, not graph-walking. plot rings are replay-assigned
from document 0's counter in log order, and explicit rings in
records bump the counters past themselves. when a record's face is
at hand, its ring tail is checked against the face's grafts. per
spec/design/genesis.md and spec/design/delta-schemas.md.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

from hwatu import deltas, layouts, sips, slurp
from hwatu.codec import parse_face
from hwatu.layouts import Ring
from hwatu.nodes import Blossom, Face, Node, Pad, Stem
from hwatu.store import Store, key_ring


@dataclass(frozen=True)
class Back:
    """a card's catalog projection: its face bloom and child rings."""

    bloom: tuple[int, ...]
    kids: tuple[Ring, ...]


@dataclass
class Orchard:
    """the mutable projections an opened orchard holds in ram."""

    name: str = ""
    plots: dict[Ring, str] = field(default_factory=dict)
    registry: dict[Ring, tuple[int, ...]] = field(default_factory=dict)
    documents: dict[Ring, Ring] = field(default_factory=dict)
    backs: dict[Ring, Back] = field(default_factory=dict)
    next_document: int = 1
    next_step: dict[int, int] = field(default_factory=dict)


def open(backing: Store) -> Orchard:
    """read + parse + replay: the orchard a store holds.

    the faces table travels as sealed bytes; the log records parse
    here, above the protocol -- the store never parses. per
    spec/store.md.
    """
    faces = tuple(value for _, value in backing.scan("faces"))
    return replay(_log(backing, "tills"), _log(backing, "flushes"), faces)


def _log(backing: Store, table: str) -> Iterator[tuple[Ring, Face]]:
    for key, value in backing.scan(table):
        yield key_ring(key), parse_face(slurp.unpack(value))


def replay(
    tills: Iterable[tuple[Ring, Face]],
    flushes: Iterable[tuple[Ring, Face]],
    faces: Iterable[bytes] = (),
) -> Orchard:
    """replay a log into an Orchard.

    tills and flushes are (stamp ring, record face) pairs; faces are
    sealed slurp bytes made resolvable by bloom for the ring-tail
    integrity check (absent faces are tolerated -- they are inert
    values, and forward references are legal).
    """
    orchard = Orchard()
    seeded = {slurp.bloom_of(data): data for data in faces}
    till_names = deltas.TILL.names()
    flush_names = deltas.FLUSH.names()
    merged = sorted(
        [(stamp, 0, record) for stamp, record in tills]
        + [(stamp, 1, record) for stamp, record in flushes],
        key=lambda entry: (entry[0], entry[1]),
    )
    for _, table, record in merged:
        act = record.root.kids[1]
        if not isinstance(act, Stem):
            continue  # future vocabularies may root differently
        if table == 0:
            _till(orchard, act, till_names.get(act.kind))
        else:
            _flush(orchard, act, flush_names.get(act.kind), seeded)
    return orchard


def _till(orchard: Orchard, act: Stem, name: str | None) -> None:
    if name == "found":
        orchard.name = _words(act)
    elif name == "plot":
        ring = _mint(orchard, 0)
        orchard.plots[ring] = _words(act)
    elif name == "stake":
        if len(act.kids) != 2:
            raise ValueError("a stake ties one ring to one bloom")
        lineage = _ring(act.kids[0])
        orchard.registry[lineage] = _bloom(act.kids[1])
        _bump(orchard, lineage)


def _flush(
    orchard: Orchard,
    act: Stem,
    name: str | None,
    seeded: dict[tuple[int, ...], bytes],
) -> None:
    if name == "sow":
        if len(act.kids) < 3:
            raise ValueError("a sow is taproot ring, plot ring, bloom")
        taproot = _ring(act.kids[0])
        plot = _ring(act.kids[1])
        bloom = _bloom(act.kids[2])
        kids = tuple(_ring(kid) for kid in act.kids[3:])
        orchard.documents[taproot] = plot
        _plant(orchard, taproot, bloom, kids, seeded)
    elif name == "shoot":
        if len(act.kids) < 2:
            raise ValueError("a shoot is stead ring, bloom")
        ring = _ring(act.kids[0])
        bloom = _bloom(act.kids[1])
        kids = tuple(_ring(kid) for kid in act.kids[2:])
        _plant(orchard, ring, bloom, kids, seeded)


def _plant(
    orchard: Orchard,
    ring: Ring,
    bloom: tuple[int, ...],
    kids: tuple[Ring, ...],
    seeded: dict[tuple[int, ...], bytes],
) -> None:
    """the shared write: the back replaced whole, counters bumped,
    the ring tail checked against the face when the face is at hand."""
    data = seeded.get(bloom)
    if data is not None:
        grafts = _graft_count(parse_face(slurp.unpack(data)))
        if grafts != len(kids):
            raise ValueError(
                f"the face at ring {ring} holds {grafts} grafts; "
                f"the record carries {len(kids)} child rings"
            )
    orchard.backs[ring] = Back(bloom, kids)
    _bump(orchard, ring)
    for kid in kids:
        _bump(orchard, kid)


def _words(act: Stem) -> str:
    words = []
    for kid in act.kids:
        if isinstance(kid, Pad):
            continue
        if not (isinstance(kid, Blossom) and kid.kind == sips.NEEM):
            raise ValueError("a name is neem words")
        words.append(layouts.text(kid.petals))
    return " ".join(words)


def _ring(node: Node) -> Ring:
    if not isinstance(node, Blossom):
        raise ValueError("a ring is a blossom")
    return layouts.halves(node.petals)


def _bloom(node: Node) -> tuple[int, ...]:
    if not (isinstance(node, Blossom) and node.kind == sips.BLOOM):
        raise ValueError("expected a bloom")
    if len(node.petals) != 64:
        raise ValueError("a bloom carries 64 petals")
    return node.petals


def _mint(orchard: Orchard, document: int) -> Ring:
    step = orchard.next_step.get(document, 1)
    orchard.next_step[document] = step + 1
    return (document, step)


def _bump(orchard: Orchard, ring: Ring) -> None:
    document, step = ring
    orchard.next_document = max(orchard.next_document, document + 1)
    current = orchard.next_step.get(document, 1)
    orchard.next_step[document] = max(current, step + 1)


def _graft_count(face: Face) -> int:
    return _grafts(face.root)


def _grafts(node: Node) -> int:
    if isinstance(node, Blossom):
        return 1 if node.kind == sips.GRAFT else 0
    if isinstance(node, Pad):
        return 0
    return sum(_grafts(kid) for kid in node.kids)
