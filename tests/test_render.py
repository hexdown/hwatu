"""the renderer against the golden walks in spec/design/speech-examples.

trees built through the passage schema (schema-resolved builders: the
tests hold no kind values at all), rendered back to the printed page.
"""

from mary_frances import BANNER, PASSAGE

from hwatu import sips
from hwatu.layouts import word
from hwatu.nodes import Blossom, Stem
from hwatu.render import render

VALUES = PASSAGE.values()


def n(kind: str, *kids) -> Stem:
    return Stem(VALUES[kind], kids)


def w(text: str) -> Blossom:
    return Blossom(sips.NEEM, word(text))


def p(text: str) -> Blossom:
    return Blossom(VALUES["prop"], word(text))


def ph(*words) -> Stem:
    return n("phrase", *words)


CAW = n("turn", n("exclamation", ph(w("caw-caw"))))


def test_card_3_the_rooster_speaks():
    card_3 = n(
        "paragraph",
        CAW,
        n(
            "statement",
            ph(p("feather"), p("flop"), w("cleared"), w("his"), w("throat")),
        ),
        CAW,
    )
    assert render(card_3, PASSAGE) == (
        "“Caw-caw!” Feather Flop cleared his throat. “Caw-caw!”"
    )


def test_exhibit_a_the_full_dialogue_sentence():
    turn = n(
        "turn",
        n("question", ph(w("is"), w("he"), w("anywhere"), w("about"))),
        n(
            "quoth",
            ph(w("inquired"), p("feather"), p("flop")),
            ph(w("looking"), w("around"), w("anxiously")),
        ),
        n(
            "statement",
            ph(p("i"), w("thought"), p("i"), w("saw"), w("him"), w("go")),
        ),
    )
    assert render(turn, PASSAGE) == (
        "“Is he anywhere about?” "
        "inquired Feather Flop, looking around anxiously. "
        "“I thought I saw him go.”"
    )


def test_exhibit_c_softening_pivot_and_elide():
    turn = n(
        "turn",
        n(
            "statement",
            ph(w("yes")),
            ph(w("he's"), w("gone")),
            ph(p("feather"), p("flop")),
        ),
        n("quoth", ph(w("laughed"), p("mary"), p("frances"))),
        n(
            "statement",
            n("pivot", w("but"), w("let"), w("me"), w("show"), w("you")),
            ph(
                w("he"),
                w("has"),
                w("been"),
                w("planning"),
                w("such"),
                w("a"),
                w("delightful"),
                w("garden"),
                w("for"),
                w("me"),
            ),
        ),
    )
    assert render(turn, PASSAGE) == (
        "“Yes, he’s gone, Feather Flop,” "
        "laughed Mary Frances. "
        "“But let me show you—he has been planning "
        "such a delightful garden for me.”"
    )


def test_exhibit_f_the_introducer():
    turn = n(
        "turn",
        n("quoth", ph(w("at"), w("length"), w("he"), w("blurted"), w("out"))),
        n(
            "broken",
            ph(w("you"), w("told"), w("me")),
            ph(w("little"), p("miss")),
            ph(p("i"), w("think")),
            ph(
                w("that"),
                w("fish-worms"),
                w("were"),
                w("good"),
                w("for"),
                w("the"),
                w("garden"),
            ),
        ),
    )
    assert render(turn, PASSAGE) == (
        "At length he blurted out, "
        "“You told me, little Miss, I think, "
        "that fish-worms were good for the garden—”"
    )


def test_the_fade_echo():
    turn = n(
        "turn",
        n("exclamation", ph(w("good-bye"))),
        n("fade", n("exclamation", ph(w("good-bye")))),
        n(
            "quoth",
            ph(w("cried"), p("feather"), p("flop")),
            ph(w("jumping"), w("off"), w("the"), w("bench")),
        ),
    )
    assert render(turn, PASSAGE) == (
        "“Good-bye! good-bye!” cried Feather Flop, jumping off the bench."
    )


def test_unknown_kinds_degrade_gracefully():
    # a kind value the schema does not name: children joined, no crash
    mystery = Stem(0o30, (ph(w("still")), ph(w("legible"))))
    assert render(mystery, PASSAGE) == "still legible"


def test_a_title_derives_its_case_with_minor_words():
    # ch47's heading shape: interior minor words stay low, the rest rise
    banner_values = BANNER.values()
    title = Stem(
        banner_values["title"],
        (w("have"), w("a"), w("seat"), w("on"), w("a"), w("toad"), w("stool")),
    )
    assert render(title, BANNER) == "Have a Seat on a Toad Stool"


def test_an_embedded_quoth_cuts_the_run():
    embedded = n(
        "turn",
        n(
            "statement",
            ph(p("i"), w("was"), w("listening")),
            n("quoth", ph(w("acknowledged"), p("feather"), p("flop"))),
            ph(w("and"), p("i"), w("don't"), w("approve")),
        ),
    )
    assert render(embedded, PASSAGE) == (
        "“I was listening,” acknowledged Feather Flop, “and I don’t approve.”"
    )
