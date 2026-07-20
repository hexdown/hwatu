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

scope: the sentence-level constructs of chapter 4. embedded quoths
(a quoth at a phrase position inside a sentence) are the next
increment, before full-chapter ingest.
"""

from . import layouts
from . import sips as s
from .nodes import Blossom, Bough, Face, Node, Pad, Stem
from .schema import Layout as LayoutSpec
from .schema import Schema

SENTENCES = {
    "statement": ".",
    "question": "?",
    "exclamation": "!",
    "broken": "—",
}


def render_face(face: Face, schema: Schema) -> str:
    return render(face.root.kids[1], schema)


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
    if name in ("phrase", "pivot"):
        return _words(node, schema, names)
    # unknown kinds degrade gracefully: children joined
    return " ".join(_node(k, schema, names) for k in node.kids)


def _blossom(node: Blossom, schema: Schema, names: dict[int, str]) -> str:
    word = layouts.text(node.petals).replace("'", "’")
    word = word.replace("*", "’")
    if node.kind == s.NEEM:
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
    """phrases joined by commas, pivots by dashes, one terminal."""
    parts: list[str] = []
    kids = node.kids
    for i, kid in enumerate(kids):
        kname = names.get(getattr(kid, "kind", -1), "")
        if kname == "quoth":
            raise NotImplementedError(
                "embedded quoths render in the next increment"
            )
        text = _node(kid, schema, names)
        if kname == "pivot":
            parts.append(text + "—")
        elif i + 1 < len(kids):
            parts.append(text + ", ")
        else:
            parts.append(text)
    text = "".join(parts)
    return text[:1].upper() + text[1:] + SENTENCES[name]


def _turn(node: Stem | Bough, schema: Schema, names: dict[int, str]) -> str:
    """the dialogue mechanics: quoted runs derived, quoths by position.

    softening: a statement's `.` renders `,` before a sentence-level
    quoth; a quoth ends `,` when it introduces (turn-initial), `.`
    otherwise; capitalization derives -- quoths stay lowercase except
    a turn-opening introducer.
    """
    out: list[str] = []
    run: list[tuple[str, str]] = []  # (rendered sentence, kind name)

    def flush(before_quoth: bool) -> None:
        if not run:
            return
        text, last = run[-1]
        if before_quoth and last == "statement":
            run[-1] = (text[:-1] + ",", last)
        out.append("“" + " ".join(t for t, _ in run) + "”")
        run.clear()

    for kid in node.kids:
        kname = names.get(getattr(kid, "kind", -1), "")
        if kname == "quoth" and isinstance(kid, Stem):
            opening = not out and not run
            flush(before_quoth=True)
            phrases = ", ".join(
                _words(p, schema, names)
                for p in kid.kids
                if isinstance(p, Stem)
            )
            if opening:
                phrases = phrases[:1].upper() + phrases[1:]
                out.append(phrases + ",")
            else:
                out.append(phrases + ".")
        else:
            run.append((_node(kid, schema, names), kname))
    flush(before_quoth=False)
    return " ".join(out)
