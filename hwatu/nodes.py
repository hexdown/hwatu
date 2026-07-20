"""the in-ram document tree: generic nodes mirroring the metastructure.

frozen dataclasses, one per kind family -- and nothing else. kinds are
numbers; semantics arrive from schemas as a view, never as python types.
face trees are content-addressed values, so nodes are immutable and
compare by content.
"""

from dataclasses import dataclass
from typing import Union

Node = Union["Stem", "Bough", "Blossom", "Pad"]


@dataclass(frozen=True)
class Stem:
    """stem-family node (b0xxxxx): children are nodes."""

    kind: int
    kids: tuple[Node, ...]


@dataclass(frozen=True)
class Bough:
    """bough-family node (b10xxxx): children must all be grafts."""

    kind: int
    kids: tuple[Node, ...]


@dataclass(frozen=True)
class Blossom:
    """blossom-family node (b11xxxx): children are petals."""

    kind: int
    petals: tuple[int, ...]


@dataclass(frozen=True)
class Pad:
    """the null node: a single sip. an intentionally empty slot when it
    appears in a child position; arena or slack at the face's edges."""


@dataclass(frozen=True)
class Face:
    """a card face: leading pads, the schema node, trailing pads.

    pad counts are part of the face's identity -- the content hash is
    computed over the whole padded stream.
    """

    lead: int
    root: Stem  # the schema node (kind SCHEMA, two kids)
    tail: int
