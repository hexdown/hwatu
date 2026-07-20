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


# the dispatch hook: layout id -> (encode, decode)
LAYOUTS = {PHONEME: (word, text), NUMERIC: (number, digits)}
