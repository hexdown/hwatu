"""chapter 4, card by card: feather flop's argument, hand-transcribed.

the trees follow spec/design/ch4-annotation.md card for card, and the
builders read like the annotation's own notation: a phrase is its
words (`^` marks a prop, `-` a beat join, `'` an elide, `*` a
possess), sentences take phrases, pivots, and quoths positionally,
turns take sentences, quoths, and fades. capitalization is never
stored; every expected rendering below is the printed source with
the decided normalizations applied.

CARDS holds every transcribed constructor by annotation number;
RENDERED holds each card's expected markdown -- the printed source
with the decided normalizations applied.
"""

import mary_frances

from hwatu import layouts, sips
from hwatu.nodes import Blossom, Bough, Face, Stem

VALUES = mary_frances.PASSAGE.values()
BLOOMS = mary_frances.blooms()


def _word(token: str) -> Blossom:
    if token.startswith("^"):
        return Blossom(VALUES["prop"], layouts.word(token[1:]))
    return Blossom(sips.NEEM, layouts.word(token))


def phrase(text: str) -> Stem:
    return Stem(VALUES["phrase"], tuple(_word(t) for t in text.split()))


def pivot(text: str) -> Stem:
    return Stem(VALUES["pivot"], tuple(_word(t) for t in text.split()))


def quoth(*texts: str) -> Stem:
    return Stem(VALUES["quoth"], tuple(phrase(t) for t in texts))


def statement(*kids: Stem) -> Stem:
    return Stem(VALUES["statement"], kids)


def question(*kids: Stem) -> Stem:
    return Stem(VALUES["question"], kids)


def exclamation(*kids: Stem) -> Stem:
    return Stem(VALUES["exclamation"], kids)


def broken(*kids: Stem) -> Stem:
    return Stem(VALUES["broken"], kids)


def turn(*kids: Stem) -> Stem:
    return Stem(VALUES["turn"], kids)


def fade(*kids: Stem) -> Stem:
    return Stem(VALUES["fade"], kids)


def passage(*kids: Stem) -> Face:
    governor = Blossom(sips.BLOOM, BLOOMS["passage"])
    root = Stem(VALUES["paragraph"], kids)
    return Face(0, Stem(sips.SCHEMA, (governor, root)), 0)


def card_1() -> Face:
    return passage(
        statement(
            phrase(
                "neither of the children had noticed the head of the "
                "big rooster as he peered curiously through the "
                "curtained window of the play house while they were "
                "talking"
            )
        )
    )


def card_2() -> Face:
    return passage(
        statement(
            phrase("as ^mary ^frances came out of the door"),
            phrase("^feather ^flop walked around the corner of the house"),
        ),
        statement(
            phrase(
                "the little girl was so absorbed in looking at the "
                "plan that she did not see the rooster"
            )
        ),
    )


def card_3() -> Face:
    return passage(
        turn(exclamation(phrase("caw-caw"))),
        statement(phrase("^feather ^flop cleared his throat")),
        turn(exclamation(phrase("caw-caw"))),
    )


def card_4() -> Face:
    return passage(
        turn(
            exclamation(
                phrase("why"),
                phrase("^feather ^flop"),
                quoth("cried ^mary ^frances"),
                phrase("how you surprised me"),
            ),
            broken(
                phrase(
                    "^i was so busy studying out ^billy*s plan for the garden"
                )
            ),
        )
    )


def card_5() -> Face:
    return passage(
        turn(
            question(phrase("is he anywhere about")),
            quoth("inquired ^feather ^flop", "looking around anxiously"),
            statement(phrase("^i thought ^i saw him go")),
        )
    )


def card_6() -> Face:
    return passage(
        turn(
            statement(
                phrase("yes"),
                phrase("he's gone"),
                phrase("^feather ^flop"),
            ),
            quoth("laughed ^mary ^frances"),
            statement(
                pivot("but let me show you"),
                phrase("he has been planning such a delightful garden for me"),
            ),
        )
    )


def card_7() -> Face:
    return passage(
        turn(
            exclamation(phrase("delightful")),
            quoth("shrilled ^feather ^flop"),
            exclamation(phrase("delightful")),
            statement(phrase("^i don't think so")),
        )
    )


def card_8() -> Face:
    return passage(
        turn(
            question(phrase("why"), phrase("what makes you say that")),
            question(phrase("how do you know what he planned")),
            quoth("inquired ^mary ^frances"),
        )
    )


def card_9() -> Face:
    return passage(
        turn(
            statement(
                phrase("^i heard every word"),
                phrase("every word"),
            ),
            quoth("said the rooster"),
            statement(
                pivot("of course you didn't see me"),
                phrase("^i was peeping in the window"),
            ),
        )
    )


def card_10() -> Face:
    return passage(
        turn(
            exclamation(phrase("oh"), phrase("^feather ^flop")),
            quoth("cried ^mary ^frances"),
            question(phrase("were you eaves-dropping")),
        )
    )


def card_11() -> Face:
    return passage(
        turn(
            statement(
                phrase("^i was listening"),
                quoth("acknowledged ^feather ^flop"),
                phrase("and ^i don't approve of the plan at all"),
            )
        )
    )


def card_12() -> Face:
    return passage(
        turn(
            question(phrase("why"), phrase("what's wrong with it")),
            quoth("asked ^mary ^frances"),
            statement(phrase("^i think it's beautiful")),
        )
    )


def card_13() -> Face:
    return passage(
        turn(
            exclamation(phrase("it's not sensible")),
            quoth("said ^feather ^flop"),
            exclamation(phrase("it's not useful")),
        )
    )


def card_14() -> Face:
    return passage(
        turn(
            statement(phrase("but it seems perfect to me")),
            question(
                phrase("how would you change it"),
                phrase("^feather ^flop"),
            ),
        )
    )


def card_15() -> Face:
    return passage(
        turn(
            exclamation(phrase("nobody can eat flowers")),
            quoth("exclaimed ^feather ^flop"),
            exclamation(
                phrase("see here"),
                quoth(
                    "he looked over ^mary ^frances* shoulder as she "
                    "sat down on the bench",
                    "and pointed with his claw",
                ),
                phrase(
                    "that plan fills the entire front yard with "
                    "bloomin' plants and gives only the little back "
                    "yard for such things as taste good"
                ),
            ),
        )
    )


def card_16() -> Face:
    return passage(
        turn(
            exclamation(phrase("dearie me")),
            exclamation(phrase("dearie me")),
            quoth("laughed ^mary ^frances"),
            question(phrase("is that it"), phrase("^feather ^flop")),
            question(
                phrase("why"),
                phrase("don't you love to see beautiful flowers"),
            ),
        )
    )


def card_17() -> Face:
    return passage(
        turn(
            statement(
                phrase(
                    "not half as much as ^i do to eat beautiful "
                    "lettuce and beet tops and other beautiful "
                    "vegetables"
                )
            ),
            quoth("declared ^feather ^flop", "shaking his head sadly"),
        )
    )


def card_18() -> Face:
    return passage(
        turn(
            statement(
                phrase("it's too bad"),
                phrase("^feather ^flop"),
                quoth("said ^mary ^frances", "smoothing his fine feathers"),
                phrase(
                    "but ^i'll see that you get plenty of such green "
                    "things as you like"
                ),
            )
        )
    )


def card_19() -> Face:
    return passage(
        turn(
            statement(
                phrase("oh"),
                phrase("thank you"),
                phrase("little ^miss"),
            ),
            quoth("said the rooster"),
            statement(
                phrase("if you will do that"),
                pivot("^i'm ready to help with your silly"),
                phrase("^i mean your brother*s"),
                phrase("plan"),
            ),
        )
    )


def card_20() -> Face:
    return passage(
        turn(
            statement(
                phrase("thank you"),
                phrase("^feather ^flop"),
                phrase("for all your help"),
                quoth("said the little girl"),
                phrase("and good-bye for now"),
            ),
            statement(
                phrase(
                    "^i must go or maybe mother will send ^billy to look for me"
                )
            ),
        )
    )


def card_21() -> Face:
    return passage(
        turn(
            exclamation(phrase("good-bye")),
            fade(exclamation(phrase("good-bye"))),
            quoth(
                "cried ^feather ^flop",
                "jumping off the bench and running away as fast as possible",
            ),
        )
    )


CARDS = {
    1: card_1,
    2: card_2,
    3: card_3,
    4: card_4,
    5: card_5,
    6: card_6,
    7: card_7,
    8: card_8,
    9: card_9,
    10: card_10,
    11: card_11,
    12: card_12,
    13: card_13,
    14: card_14,
    15: card_15,
    16: card_16,
    17: card_17,
    18: card_18,
    19: card_19,
    20: card_20,
    21: card_21,
}

RENDERED = {
    1: (
        "Neither of the children had noticed the head of the big "
        "rooster as he peered curiously through the curtained window "
        "of the play house while they were talking."
    ),
    2: (
        "As Mary Frances came out of the door, Feather Flop walked "
        "around the corner of the house. The little girl was so "
        "absorbed in looking at the plan that she did not see the "
        "rooster."
    ),
    3: "“Caw-caw!” Feather Flop cleared his throat. “Caw-caw!”",
    5: (
        "“Is he anywhere about?” inquired Feather Flop, looking "
        "around anxiously. “I thought I saw him go.”"
    ),
    6: (
        "“Yes, he’s gone, Feather Flop,” laughed Mary Frances. “But "
        "let me show you—he has been planning such a delightful "
        "garden for me.”"
    ),
    7: "“Delightful!” shrilled Feather Flop. “Delightful! I don’t think so.”",
    8: (
        "“Why, what makes you say that? How do you know what he "
        "planned?” inquired Mary Frances."
    ),
    9: (
        "“I heard every word, every word,” said the rooster. “Of "
        "course you didn’t see me—I was peeping in the window.”"
    ),
    10: "“Oh, Feather Flop!” cried Mary Frances. “Were you eaves-dropping?”",
    4: (
        "“Why, Feather Flop,” cried Mary Frances, “how you surprised "
        "me! I was so busy studying out Billy’s plan for the garden—”"
    ),
    11: (
        "“I was listening,” acknowledged Feather Flop, “and I don’t "
        "approve of the plan at all.”"
    ),
    12: (
        "“Why, what’s wrong with it?” asked Mary Frances. “I think "
        "it’s beautiful.”"
    ),
    13: "“It’s not sensible!” said Feather Flop. “It’s not useful!”",
    14: (
        "“But it seems perfect to me. How would you change it, Feather Flop?”"
    ),
    15: (
        "“Nobody can eat flowers!” exclaimed Feather Flop. “See "
        "here,” he looked over Mary Frances’ shoulder as she sat "
        "down on the bench, and pointed with his claw, “that plan "
        "fills the entire front yard with bloomin’ plants and gives "
        "only the little back yard for such things as taste good!”"
    ),
    16: (
        "“Dearie me! Dearie me!” laughed Mary Frances. “Is that it, "
        "Feather Flop? Why, don’t you love to see beautiful "
        "flowers?”"
    ),
    17: (
        "“Not half as much as I do to eat beautiful lettuce and "
        "beet tops and other beautiful vegetables,” declared Feather "
        "Flop, shaking his head sadly."
    ),
    18: (
        "“It’s too bad, Feather Flop,” said Mary Frances, smoothing "
        "his fine feathers, “but I’ll see that you get plenty of "
        "such green things as you like.”"
    ),
    19: (
        "“Oh, thank you, little Miss,” said the rooster. “If you "
        "will do that, I’m ready to help with your silly—I mean "
        "your brother’s, plan.”"
    ),
    20: (
        "“Thank you, Feather Flop, for all your help,” said the "
        "little girl, “and good-bye for now. I must go or maybe "
        "mother will send Billy to look for me.”"
    ),
    21: (
        "“Good-bye! good-bye!” cried Feather Flop, jumping off the "
        "bench and running away as fast as possible."
    ),
}

# the banner: our first quant, under the chapter-banner convention

BANNER_VALUES = mary_frances.BANNER.values()


def banner() -> Face:
    governor = Blossom(sips.BLOOM, BLOOMS["banner"])
    title = Stem(
        BANNER_VALUES["title"],
        (
            Blossom(sips.NEEM, layouts.word("chapter")),
            Blossom(BANNER_VALUES["quant"], layouts.number("4")),
            Blossom(BANNER_VALUES["prop"], layouts.word("feather")),
            Blossom(BANNER_VALUES["prop"], layouts.word("flop*s")),
            Blossom(sips.NEEM, layouts.word("argument")),
        ),
    )
    return Face(0, Stem(sips.SCHEMA, (governor, title)), 0)


BANNER_RENDERED = "Chapter 4. Feather Flop’s Argument"

# the branch cards: boughs over grafts, no content of their own

SECTION_VALUES = mary_frances.SECTION.values()
TAPROOT_VALUES = mary_frances.TAPROOT.values()


def _graft(kind_value: int) -> Blossom:
    return Blossom(sips.GRAFT, (kind_value,))


def section_card() -> Face:
    """the chapter's body: one banner graft, then the 21 passages."""
    governor = Blossom(sips.BLOOM, BLOOMS["section"])
    bough = Bough(
        SECTION_VALUES["section"],
        (
            _graft(SECTION_VALUES["banner"]),
            *(_graft(SECTION_VALUES["passage"]) for _ in range(21)),
        ),
    )
    return Face(0, Stem(sips.SCHEMA, (governor, bough)), 0)


def taproot_card() -> Face:
    """the document's anchor: a single section graft."""
    governor = Blossom(sips.BLOOM, BLOOMS["taproot"])
    bough = Bough(
        TAPROOT_VALUES["taproot"],
        (_graft(TAPROOT_VALUES["section"]),),
    )
    return Face(0, Stem(sips.SCHEMA, (governor, bough)), 0)
