"""serialize and deserialize: node trees <-> sip sequences.

free functions over the frozen dataclasses in nodes.py. parsing never
fails on complete streams (structure is public grammar); truncation
errors say exactly what the count sips still expect. semantic
validation against schemas is a separate concern, not performed here.
"""

from . import sips as s
from .nodes import Blossom, Bough, Face, Node, Pad, Stem


class Truncated(Exception):
    """the stream ended while a count sip still expected children."""


def encode(node: Node) -> tuple[int, ...]:
    """serialize one node (recursively) to sips."""
    if isinstance(node, Pad):
        return (s.NULL,)
    if isinstance(node, Blossom):
        _check_count(node.kind, len(node.petals))
        return (node.kind, len(node.petals) - 1, *node.petals)
    _check_count(node.kind, len(node.kids))
    out = [node.kind, len(node.kids) - 1]
    for kid in node.kids:
        out.extend(encode(kid))
    return tuple(out)


def parse(stream: tuple[int, ...], at: int = 0) -> tuple[Node, int]:
    """deserialize one node starting at index `at`.

    returns the node and the index just past it. the five-line grammar:
    null -> pad; blossom -> petals; branch and stem -> recurse.
    """
    kind = _take(stream, at, "a kind sip")
    if kind == s.NULL:
        return Pad(), at + 1
    count = _take(stream, at + 1, f"a count sip for kind {kind:#o}") + 1
    at += 2
    if kind >= 0o60:  # blossom family: petals, flat
        if at + count > len(stream):
            raise Truncated(
                f"blossom {kind:#o} expects {count} petals, "
                f"stream ends after {len(stream) - at}"
            )
        return Blossom(kind, tuple(stream[at : at + count])), at + count
    kids = []
    for n in range(count):
        try:
            kid, at = parse(stream, at)
        except Truncated as e:
            raise Truncated(
                f"child {n + 1} of {count} under kind {kind:#o}: {e}"
            ) from None
        kids.append(kid)
    node = Bough if kind >= 0o40 else Stem
    return node(kind, tuple(kids)), at


def encode_face(face: Face) -> tuple[int, ...]:
    return (s.NULL,) * face.lead + encode(face.root) + (s.NULL,) * face.tail


def parse_face(stream: tuple[int, ...]) -> Face:
    """parse a whole face: pads, one schema node, pads, nothing else."""
    lead = 0
    while lead < len(stream) and stream[lead] == s.NULL:
        lead += 1
    if lead == len(stream):
        raise ValueError("a face needs a schema node; found only pads")
    root, at = parse(stream, lead)
    if not (isinstance(root, Stem) and root.kind == s.SCHEMA):
        found = stream[lead]  # the kind sip we actually saw
        raise ValueError(
            f"a face opens with the schema node ({s.SCHEMA:#o}); "
            f"found kind {found:#o}"
        )
    tail = len(stream) - at
    if any(v != s.NULL for v in stream[at:]):
        raise ValueError("only pads may follow the schema node")
    return Face(lead, root, tail)


def _take(stream: tuple[int, ...], at: int, wanted: str) -> int:
    if at >= len(stream):
        raise Truncated(f"stream ends where {wanted} was expected")
    return stream[at]


def _check_count(kind: int, n: int) -> None:
    if not 1 <= n <= 64:
        raise ValueError(f"kind {kind:#o} has {n} children; nodes hold 1-64")
