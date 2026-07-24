"""petal layouts: interpretations of petal sequences, by layout id.

the metastructure never interprets a petal; a blossom kind names its
layout (via the metaschema's `layout` spec) and this module implements
the closed set the core ships. schemas select layouts from this set --
they do not define new ones; extension layouts would claim ids from
the reserve, a spec event rather than configuration.
"""

from hwatu import sips

PHONEME = 0  # neem, prop: base-36 alphanumerics plus the small marks
NUMERIC = 1  # quant: decimal digits, one petal per digit (d = value d)
RING = 2  # ring: a 6+4 id in ten raw petals (high 36 bits, low 24)

_WORD_MARKS = {"-": sips.BEAT, "'": sips.ELIDE, "*": sips.POSSESS}
_MARK_CHARS = {v: k for k, v in _WORD_MARKS.items()}


def word(text: str) -> tuple[int, ...]:
    """phoneme-layout petals for a word.

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
    """the word a phoneme-layout petal sequence spells."""
    chars = []
    for p in petals:
        if p in _MARK_CHARS:
            chars.append(_MARK_CHARS[p])
        elif 0 <= p < 36:
            chars.append(sips.GLYPHS[p])
        else:
            raise ValueError(f"petal {p:#o} is not a phoneme petal")
    return "".join(chars)


def number(digits_text: str) -> tuple[int, ...]:
    """numeric-layout petals: one petal per decimal digit."""
    return tuple(int(ch) for ch in digits_text)


def digits(petals: tuple[int, ...]) -> str:
    """the decimal number a numeric-layout petal sequence spells."""
    if any(not 0 <= p <= 9 for p in petals):
        raise ValueError("numeric petals are decimal digits")
    return "".join(str(p) for p in petals)


def ring(high: int, low: int) -> tuple[int, ...]:
    """ring-layout petals: a 6+4 id as six high petals, four low.

    the high half is a document-id or a stamp (36 bits), the low half
    a local-id or a counter (24 bits) -- card rings and stamp rings
    share the shape.
    """
    if not 0 <= high < 1 << 36:
        raise ValueError(f"a ring's high half holds 36 bits; got {high}")
    if not 0 <= low < 1 << 24:
        raise ValueError(f"a ring's low half holds 24 bits; got {low}")
    highs = tuple((high >> (6 * n)) & 0o77 for n in reversed(range(6)))
    lows = tuple((low >> (6 * n)) & 0o77 for n in reversed(range(4)))
    return highs + lows


def halves(petals: tuple[int, ...]) -> tuple[int, int]:
    """the (high, low) pair a ring-layout petal sequence spells."""
    if len(petals) != 10 or any(not 0 <= p < 64 for p in petals):
        raise ValueError("a ring is ten petals")
    high = 0
    for petal in petals[:6]:
        high = (high << 6) | petal
    low = 0
    for petal in petals[6:]:
        low = (low << 6) | petal
    return high, low


def pair(petals: tuple[int, ...]) -> str:
    """a ring's display form: the spelled "(high, low)" pair."""
    high, low = halves(petals)
    return f"({high}, {low})"


# the dispatch hook: layout id -> (encode, decode); decode always
# yields display text -- ring work goes through halves, and ring's
# encoder takes the (high, low) pair rather than text
LAYOUTS = {
    PHONEME: (word, text),
    NUMERIC: (number, digits),
    RING: (ring, pair),
}
