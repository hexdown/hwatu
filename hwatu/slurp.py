"""slurps: sip sequences packed to canonical bytes, and their blooms.

a slurp is a contiguous block of packed sips sized in 24-byte
increments (32 sips each), minimum one increment, maximum sixty
(1440 bytes / 1920 sips) -- hwatu/design/store.md. within a slurp:
leading beats are the collision-resolution arena, then content, then
trailing beats of slack. the content hash -- a card's bloom -- is
blake2b-384 over the whole slurp byte stream: exactly 64 petals.

packing is big-endian 6-bit: four sips to three bytes. the slurp
bytes are the canonical, identity-bearing form of a face; trees and
sip tuples are working forms.
"""

import hashlib

from hwatu import sips

INCREMENT_SIPS = 32  # 24 bytes = 192 bits = three 64-bit words
MAX_SIPS = 1920  # 60 increments; fits a network packet payload


def fit(content: tuple[int, ...], lead: int = 0) -> tuple[int, ...]:
    """size a slurp: lead arena beats, content, slack to an increment."""
    used = lead + len(content)
    if used > MAX_SIPS:
        raise ValueError(
            f"{used} sips exceeds the {MAX_SIPS}-sip slurp maximum; "
            "fragment the content into more cards upstream"
        )
    total = max(1, -(-used // INCREMENT_SIPS)) * INCREMENT_SIPS
    tail = total - used
    return (sips.NULL,) * lead + content + (sips.NULL,) * tail


def pack(slurp: tuple[int, ...]) -> bytes:
    """four sips to three bytes, big-endian 6-bit groups."""
    if len(slurp) % 4:
        raise ValueError("slurps pack in groups of four sips")
    out = bytearray()
    for i in range(0, len(slurp), 4):
        a, b, c, d = slurp[i : i + 4]
        group = (a << 18) | (b << 12) | (c << 6) | d
        out.extend(group.to_bytes(3))
    return bytes(out)


def unpack(data: bytes) -> tuple[int, ...]:
    """three bytes back to four sips."""
    if len(data) % 3:
        raise ValueError("packed slurps come in three-byte groups")
    out = []
    for i in range(0, len(data), 3):
        group = int.from_bytes(data[i : i + 3])
        out.extend(
            (
                (group >> 18) & 63,
                (group >> 12) & 63,
                (group >> 6) & 63,
                group & 63,
            )
        )
    return tuple(out)


def bloom_of(data: bytes) -> tuple[int, ...]:
    """the content hash as 64 petals: blake2b-384 over the slurp bytes."""
    digest = hashlib.blake2b(data, digest_size=48).digest()
    number = int.from_bytes(digest)
    return tuple((number >> (6 * (63 - i))) & 63 for i in range(64))


def seal(content: tuple[int, ...]) -> bytes:
    """content sips to canonical slurp bytes (no arena, fresh slack)."""
    return pack(fit(content))


def redistribute(slurp: tuple[int, ...]) -> tuple[int, ...]:
    """resolve a bloom collision: shift one slack beat to the arena,
    growing the slurp by an increment when the slack is spent."""
    lead = 0
    while lead < len(slurp) and slurp[lead] == sips.NULL:
        lead += 1
    tail = 0
    while tail < len(slurp) and slurp[-1 - tail] == sips.NULL:
        tail += 1
    content = slurp[lead : len(slurp) - tail]
    if tail > 0:
        return fit(content, lead + 1)
    if len(slurp) + INCREMENT_SIPS > MAX_SIPS:
        raise ValueError("collision arena exhausted at maximum slurp size")
    return (
        (sips.NULL,) * (lead + 1)
        + content
        + (sips.NULL,) * (INCREMENT_SIPS - 1)
    )
