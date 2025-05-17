from collections import namedtuple
from fractions import Fraction

Cycle = namedtuple('Cycle', ['children'])
Event = namedtuple('Event', ['value', 'start', 'end'], defaults=[-1, -1])

def expand_alternatives(s):
    """
    Recursively expands out all alternative cycles by making copies of the whole string
    starting with the most deeply nested alternative cycles.
    """
    start = None
    end = None

    # find the first complete angle bracket pair, a.k.a. the first one that doesn't
    # have another nested within it
    for (i, c) in enumerate(s):
        if c == "<":
            start = i
        elif c == ">":
            end = i+1
            break

    if start is not None and end is not None:
        alternative_cycle = s[start:end]
        cycle_elements = alternative_cycle.strip("<>").split(" ")
        copies = [
            expand_alternatives(f"{s[:start]}{element}{s[end:]}") for element in cycle_elements
        ]
        return " ".join(copies)
    else:
        return s

def parse_mini(s):
    cycles = []
    stack = []
    literal = ""

    expanded = expand_alternatives(s)
    for c in expanded:
        if c == "[":
            cycle = Cycle([])

            if len(stack) > 0:
                stack[-1].children.append(cycle)

            stack.append(cycle)
        elif c in {" ", "\n", "\t", "]"}:
            if literal:
                notes = [Event(value=s) for s in literal.split(",")]
                stack[-1].children.append(notes)
                literal = ""

            if c == "]":
                node = stack.pop()

                if len(stack) == 0:
                    cycles.append(node)
        else:
            literal += c

    if len(stack) > 0:
        raise Exception(f"Unbalanced brackets in {s}")

    return cycles

def merge_voice_lists(a, b):
    """
    Merge a and b which are both 2d list of events per voice.

    Returns a new list rather than mutating a or b.
    """
    merged = [ [] for i in range(max(len(a), len(b))) ]

    for (i, merged_voice) in enumerate(merged):
        if i < len(a):
            merged_voice += a[i]
        if i < len(b):
            merged_voice += b[i]

    return merged

def generate_events(cycles):
    """
    Generate events per voice for a list of cycles.
    """
    voices = []
    for (i, cycle) in enumerate(cycles):
        voices = merge_voice_lists(
            voices,
            generate_node_events(cycle, Fraction(i), Fraction(i+1))
        )

    return voices

def generate_node_events(node, start, end):
    """
    Generate events for a single node in the parse tree.
    """

    if isinstance(node, list):
        # assumes all lists contain Events
        # returns a 2D list because each simultaneous event gets its own voice
        return [[Event(value=e.value, start=start, end=end)] for e in node]
    elif isinstance(node, Cycle):
        time_increment = (end - start) / len(node.children)
        voices = []
        for (i, child) in enumerate(node.children):
            voices = merge_voice_lists(
                voices,
                generate_node_events(
                    child,
                    start + (time_increment * i),
                    start + (time_increment * (i + 1))
                )
            )

        return voices
    else:
        raise Exception(f"unexpected node: {node}")

def split_events_by_voice(events):
    # never mind, let's do this in generate_events
    pass

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

