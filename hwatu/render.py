"""markdown from faces: rendering is code, forever separate from cards.

render(node, schema) walks a face's tree with the schema as its
dictionary: kind values resolve to names, petals decode under each
blossom kind's layout, and a rulebook keyed by kind name applies the
render rules the flora specifies. unknown kinds degrade gracefully --
children joined -- in the tree-sitter spirit.

markdown-facing conventions: elide and possess render as U+2019,
quoted runs wear curly double quotes, capitalization is derived
(sentence-initial, props, fade suppression), and the dialogue
mechanics live entirely under the turn (spec/design/speech-examples).

scope: chapter 4's dialogue, sentence-level and embedded. remaining
before the full-chapter pass: the banner title convention and
document-level assembly.
"""

from collections.abc import Callable

from hwatu import layouts, sips, slurp
from hwatu.codec import parse_face
from hwatu.layouts import Ring
from hwatu.nodes import Blossom, Bough, Face, Node, Pad, Stem
from hwatu.orchard import Orchard
from hwatu.schema import Layout as LayoutSpec
from hwatu.schema import Schema, load

SENTENCES = {
    "statement": ".",
    "question": "?",
    "exclamation": "!",
    "broken": "—",
}


def render_face(face: Face, schema: Schema) -> str:
    return render(face.root.kids[1], schema)


def render_document(
    grove: Orchard,
    taproot: Ring,
    fetch: Callable[[tuple[int, ...]], bytes | None],
) -> str:
    """markdown for a whole document, walked from its taproot.

    branch cards contribute structure: their backs' child rings walk
    in graft order. leaf cards contribute blocks: each face fetched
    by bloom, its schema fetched by the face's own governor bloom,
    rendered under that schema. a banner's heading marks derive from
    its depth in the card tree (the book layer may revisit), blocks
    join on blank lines, and the document closes with a rule.
    """
    blocks: list[str] = []

    def walk(ring: Ring, depth: int) -> None:
        back = grove.backs[ring]
        if back.kids:
            for kid in back.kids:
                walk(kid, depth + 1)
            return
        face = parse_face(slurp.unpack(_fetched(fetch, back.bloom)))
        governor = face.root.kids[0]
        if not isinstance(governor, Blossom):
            raise ValueError("a face opens with its schema bloom")
        speaks = load(slurp.unpack(_fetched(fetch, governor.petals)))
        text = render_face(face, speaks)
        if speaks.name == "banner":
            text = "#" * depth + " " + text
        blocks.append(text)

    walk(taproot, 0)
    blocks.append("---")
    return "\n\n".join(blocks) + "\n"


def _fetched(
    fetch: Callable[[tuple[int, ...]], bytes | None],
    bloom: tuple[int, ...],
) -> bytes:
    data = fetch(bloom)
    if data is None:
        raise ValueError("a document's faces must be at hand to render")
    return data


def render(node: Node, schema: Schema) -> str:
    return _node(node, schema, schema.names())


def _node(node: Node, schema: Schema, names: dict[int, str]) -> str:
    if isinstance(node, Pad):
        return ""
    if isinstance(node, Blossom):
        return _blossom(node, schema, names)
    name = names.get(node.kind, "")
    if name == "paragraph":
        return " ".join(_node(k, schema, names) for k in node.kids)
    if name == "turn":
        return _turn(node, schema, names)
    if name in SENTENCES:
        return _sentence(node, name, schema, names)
    if name == "fade":
        text = " ".join(_node(k, schema, names) for k in node.kids)
        return text[:1].lower() + text[1:]
    if name == "title":
        return _title(node, schema, names)
    if name in ("phrase", "pivot"):
        return _words(node, schema, names)
    # unknown kinds degrade gracefully: children joined
    return " ".join(_node(k, schema, names) for k in node.kids)


def _blossom(node: Blossom, schema: Schema, names: dict[int, str]) -> str:
    word = layouts.text(node.petals).replace("'", "’")
    word = word.replace("*", "’")
    if node.kind == sips.NEEM:
        return word
    name = names.get(node.kind, "")
    if name == "prop":
        return word[:1].upper() + word[1:]
    kind = schema.kind(name) if name else None
    if kind is not None and isinstance(kind.spec, LayoutSpec):
        decode = layouts.LAYOUTS[kind.spec.layout][1]
        return decode(node.petals)
    return word


def _words(node: Stem | Bough, schema: Schema, names: dict[int, str]) -> str:
    return " ".join(_node(k, schema, names) for k in node.kids)


def _sentence(
    node: Stem | Bough, name: str, schema: Schema, names: dict[int, str]
) -> str:
    """a sentence outside a turn: its pieces joined plainly."""
    return " ".join(text for _, text in _pieces(node, name, schema, names))


def _pieces(
    node: Stem | Bough, name: str, schema: Schema, names: dict[int, str]
) -> list[tuple[str, str]]:
    """a sentence as alternating speech and tag pieces.

    phrases join on commas, pivots on dashes; an embedded quoth cuts
    a tag between speech pieces. the derived sentence-initial capital
    lands on the first speech piece and the terminal on the last; a
    tag carries neither -- its seam commas belong to the turn.
    """
    pieces: list[tuple[str, str]] = []
    parts: list[str] = []

    def cut() -> None:
        pieces.append(("speech", "".join(parts).removesuffix(", ")))
        parts.clear()

    for kid in node.kids:
        kname = names.get(getattr(kid, "kind", -1), "")
        if kname == "quoth" and isinstance(kid, Stem):
            cut()
            pieces.append(("tag", _quoth_text(kid, schema, names)))
            continue
        text = _node(kid, schema, names)
        parts.append(text + ("—" if kname == "pivot" else ", "))
    cut()
    first_role, first_text = pieces[0]
    pieces[0] = (first_role, first_text[:1].upper() + first_text[1:])
    last_role, last_text = pieces[-1]
    pieces[-1] = (last_role, last_text + SENTENCES[name])
    return pieces


MINOR = frozenset("a an the and but or nor of on in at to for by".split())


def _title(node: Stem | Bough, schema: Schema, names: dict[int, str]) -> str:
    """the banner convention: derived title case -- the first word,
    the last word, and every non-minor word capitalize -- and a
    numbering quant takes a trailing period ("Chapter 4. ...")."""
    words: list[str] = []
    kids = node.kids
    for i, kid in enumerate(kids):
        text = _node(kid, schema, names)
        kname = names.get(getattr(kid, "kind", -1), "")
        if kname == "quant":
            words.append(text + ".")
            continue
        interior = 0 < i < len(kids) - 1
        if not (interior and text in MINOR):
            text = text[:1].upper() + text[1:]
        words.append(text)
    return " ".join(words)


def _quoth_text(node: Stem, schema: Schema, names: dict[int, str]) -> str:
    return ", ".join(
        _words(kid, schema, names) for kid in node.kids if isinstance(kid, Stem)
    )


def _turn(node: Stem | Bough, schema: Schema, names: dict[int, str]) -> str:
    """the dialogue mechanics: quoted runs derived, quoths by position.

    a sentence-level quoth stands between sentences: it softens a
    preceding statement's period to a comma, ends with a comma when
    it opens the turn (the introducer, capitalized), a period
    otherwise. an embedded quoth interrupts a sentence mid-run: the
    run closes on a bare comma, the tag rides outside the quotes
    ending with a comma, and the reopened run carries the sentence's
    terminal when it lands. capitalization derives throughout.
    """
    out: list[str] = []
    run: list[str] = []

    def flush(at_seam: bool) -> None:
        if not run:
            return
        text = " ".join(run)
        if at_seam:
            if text.endswith("."):
                text = text[:-1] + ","  # soften a statement
            elif not text.endswith((",", "!", "?", "—")):
                text += ","  # an embedded cut: bare pre-piece
        out.append("“" + text + "”")
        run.clear()

    for kid in node.kids:
        kname = names.get(getattr(kid, "kind", -1), "")
        if kname == "quoth" and isinstance(kid, Stem):
            opening = not out and not run
            flush(at_seam=True)
            tag = _quoth_text(kid, schema, names)
            if opening:
                out.append(tag[:1].upper() + tag[1:] + ",")
            else:
                out.append(tag + ".")
        elif kname in SENTENCES and isinstance(kid, Stem):
            for role, text in _pieces(kid, kname, schema, names):
                if role == "tag":
                    flush(at_seam=True)
                    out.append(text + ",")
                else:
                    run.append(text)
        else:
            run.append(_node(kid, schema, names))
    flush(at_seam=False)
    return " ".join(out)
