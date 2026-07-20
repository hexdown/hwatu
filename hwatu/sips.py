"""sip values, kind families, and the glyph table.

the 6-bit value space per spec/glyphs.md: four kind families by leading
bits, base-36 petals, and one display glyph per value. pure data and
functions -- no classes, no state.
"""

from enum import Enum

# reserved kind values (fixed in every context, forever)
SCHEMA = 0o00  # opens every face: bloom + card root
NEEM = 0o74  # the universal phonetic word
GRAFT = 0o75  # joins a child card; exactly one petal
BLOOM = 0o76  # hash vector; 64 petals = 384 bits
NULL = 0o77  # the pad: single sip, no count, no children

# the small marks (petal meanings of the top seats)
ELIDE = 0o75  # haven't, goin'
POSSESS = 0o76  # flop*s, toads*
BEAT = 0o77  # compound join, null petal, padding


class Family(Enum):
    """kind families by leading bits (spec/glyphs.md).

    "branch" is a card-level word -- branch cards have bough-family
    roots; the kind family is named for the bough itself.
    """

    STEM = "stem"  # b0xxxxx: children are nodes
    BOUGH = "bough"  # b10xxxx: children must all be grafts
    BLOSSOM = "blossom"  # b11xxxx: children are petals
    PAD = "pad"  # b111111: the null sip's single-sip node


def family(kind: int) -> Family:
    if kind == NULL:
        return Family.PAD
    if kind >= 0o60:
        return Family.BLOSSOM
    if kind >= 0o40:
        return Family.BOUGH
    return Family.STEM


# display glyphs, one per value, per the table in spec/glyphs.md
GLYPHS = (
    "0123456789"  # 0o00-0o11: stem seats / digit petals
    "abcdefghijklmnopqrstuv"  # 0o12-0o37: stem seats / letter petals
    "wxyz"  # 0o40-0o43: branch seats / letter petals
    "βΓΔθλμΞπΣφψΩ"  # 0o44-0o57: branch seats (boughs wear greek)
    ":!?&$%@#~±=^"  # 0o60-0o73: blossom seats
    "·'*-"  # 0o74-0o77: neem, graft/elide, bloom/possess, null/beat
)
assert len(GLYPHS) == 64

VALUES = {g: v for v, g in enumerate(GLYPHS)}


def glyphs(sips: tuple[int, ...]) -> str:
    """render a sip sequence in the visible form."""
    return "".join(GLYPHS[s] for s in sips)


def sips(text: str) -> tuple[int, ...]:
    """read a visible-form string back to sip values."""
    return tuple(VALUES[g] for g in text)


# petals: alphanumerics are base-36; the small marks join them in words
_WORD_MARKS = {"-": BEAT, "'": ELIDE, "*": POSSESS}
_MARK_CHARS = {v: k for k, v in _WORD_MARKS.items()}


def word(text: str) -> tuple[int, ...]:
    """petals for a word: base-36 letters and digits plus small marks.

    beat joins compounds (caw-caw), elide marks omission (haven't),
    possess marks the genitive (flop*s).
    """
    petals = []
    for ch in text:
        if ch in _WORD_MARKS:
            petals.append(_WORD_MARKS[ch])
        else:
            petals.append(int(ch, 36))
    return tuple(petals)


def text(petals: tuple[int, ...]) -> str:
    """the word a petal sequence spells (inverse of word())."""
    chars = []
    for p in petals:
        if p in _MARK_CHARS:
            chars.append(_MARK_CHARS[p])
        elif 0 <= p < 36:
            chars.append(GLYPHS[p])
        else:
            raise ValueError(f"petal {p:#o} is not a word petal")
    return "".join(chars)
