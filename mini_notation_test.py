from fractions import Fraction

from mini_notation import Cycle, Event, parse_mini, expand_alternatives, generate_events

def test(name, expected, actual):
    if expected == actual:
        print(f"PASSED: {name}")
    else:
        print(f"FAILED: {name}\nexpected: {expected}\nactual: {actual}")

def test_raises(name, func, param):
    try:
        func(param)
    except:
        print(f"PASSED: {name}")
    else:
        print(f"FAILED: {name} No exception thrown!")

test(
    "one level, one cycle",
    [
        Cycle([ 
               [Event("a")], 
               [Event("b")], 
               [Event("c")], 
        ])
    ],
    parse_mini("[a b c]")
)

test(
    "one level, three cycles",
    [
        Cycle([[Event("a")]]),
        Cycle([[Event("b")]]),
        Cycle([[Event("c")]]),
    ],
    parse_mini("<[a] [b] [c]>")
)

test(
    "three level nesting",
    [
        Cycle([
            [Event("a")], 
            [Event("b")], 
            [Event("c")], 
        ]),
        Cycle([
            [Event("a")], 
            [Event("b")], 
            Cycle([
                [Event("c")], 
                [Event("d")], 
            ])
        ])
    ],
    parse_mini("[ a b c ] [a b [c d]]")
)

test(
    "crazy whitespace",
    [
        Cycle([
            [Event("a")], 
            [Event("b")], 
            [Event("c")], 
        ])
    ],
    parse_mini(""" [ a       b c
          ] """)
)

test(
    "polyphony",
    [
        Cycle([
            [Event("a")],
            [Event("b"), Event("c"), Event("d")],
            [Event("c"), Event("e")],
        ])
    ],
    parse_mini("[a b,c,d c,e]")
)

test_raises("test open without close", parse_mini, "[a b c")
test_raises("close without open", parse_mini, "a b c]")
test_raises("top level without brackets", parse_mini, "a b c")

test(
    "expand simple AC",
    "[a b c] [a b d]",
    expand_alternatives("[a b <c d>]")
)

test(
    "expand non-nested ACs",
    "[a b c [e f]] [a b c [e g]] [a b d [e f]] [a b d [e g]]",
    expand_alternatives("[a b <c d> [e <f g>]]")
)

test(
    "expand nested ACs",
    "[a b c] [a b d] [a b c] [a b e]",
    expand_alternatives("[a b <c <d e>>]")
)

test(
    "simple generation",
    [
        [
            Event('a', Fraction(0, 1), Fraction(1, 3)),
            Event('b', Fraction(1, 3), Fraction(2, 3)),
            Event('c', Fraction(2, 3), Fraction(1, 1))
        ]
    ],
    generate_events(parse_mini("[a b c]"))
)

test(
    "nested generation",
    [
        [
            Event('a', Fraction(0, 1), Fraction(1, 4)),
            Event('b', Fraction(1, 4), Fraction(1, 2)),
            Event('c', Fraction(1, 2), Fraction(1, 1))
        ]
    ],
    generate_events(parse_mini("[[a b] c]"))
)


test(
    "simple alternatives",
    [
        [
            Event('a', Fraction(0, 1), Fraction(1, 1)),
            Event('b', Fraction(1, 1), Fraction(2, 1)),
            Event('c', Fraction(2, 1), Fraction(3, 1))
        ]
    ],
    generate_events(parse_mini("<[a] [b] [c]>"))
)

test(
    "polyphony generation",
    [
        [
            Event("a", Fraction(0, 1), Fraction(1, 3)),
            Event("b", Fraction(1, 3), Fraction(2, 3)),
            Event("d", Fraction(2,3), Fraction(1, 1)),
        ],
        [
            Event("c", Fraction(1, 3), Fraction(2, 3)),
            Event("e", Fraction(2,3), Fraction(1, 1)),
        ],
        [
            Event("d", Fraction(1, 3), Fraction(2, 3)),
        ],
    ],
    generate_events(parse_mini("[a b,c,d d,e]"))
)

test_raises("test open without close", parse_mini, "[a b c")
test_raises("close without open", parse_mini, "a b c]")
test_raises("top level without brackets", parse_mini, "a b c")

