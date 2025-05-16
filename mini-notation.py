from fractions import Fraction

class Cycle():
    def __init__(self, children=None):
        self.children = children or []

    def __eq__(self, other):
        return self.children == other.children

    def __repr__(self):
        return "Cycle: " + repr(self.children)

class Notes():
    def __init__(self, notes=None):
        self.notes = notes or []

    def __eq__(self, other):
        if not isinstance(other, Notes):
            return False
        return self.notes == other.notes

    def __repr__(self):
        return "Notes: "+repr(self.notes)


def preprocess(s):
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
            preprocess(f"{s[:start]}{element}{s[end:]}") for element in cycle_elements
        ]
        return " ".join(copies)
    else:
        return s

def parse(s):
    cycles = []
    stack = []
    literal = ""

    for c in s:
        if c == "[":
            cycle = Cycle()

            if len(stack) > 0:
                stack[-1].children.append(cycle)

            stack.append(cycle)
        elif c in {" ", "\n", "\t", "]"}:
            if literal:
                notes = Notes(literal.split(","))
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

# TODO: fix name: not really generating nodes, generating events
def generate_nodes(nodes):
    events = []
    for (i, node) in enumerate(nodes):
        events += generate_node(node, Fraction(i), Fraction(i+1))

    return events

def generate_node(node, start, end):
    if isinstance(node, Notes):
        return (node.notes, start, end)
    elif isinstance(node, Cycle):
        time_increment = (end - start) / len(node.children)
        notes = []
        for (i, child) in enumerate(node.children):
            generated = generate_node(
                child,
                start + (time_increment * i),
                start + (time_increment * (i + 1))
            )
            if isinstance(generated, list):
                notes += generated
            elif isinstance(generated, tuple):
                notes.append(generated)
            else:
                raise Exception(f"generate_node() returned value: {generated}")

        return notes
    else:
        raise Exception(f"unexpected node: {node}")

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
    [Cycle([ Notes(["a"]), Notes(["b"]), Notes(["c"]), ])],
    parse(preprocess("[a b c]"))
)

test(
    "one level, three cycles",
    [
        Cycle([Notes(["a"])]),
        Cycle([Notes(["b"])]),
        Cycle([Notes(["c"])]),
    ],
    parse(preprocess("<[a] [b] [c]>"))
)

test(
    "three level nesting",
    [
        Cycle([
            Notes(["a"]), 
            Notes(["b"]),
            Notes(["c"])
        ]),
        Cycle([
            Notes(["a"]),
            Notes(["b"]),
            Cycle([
                Notes(["c"]), 
                Notes(["d"])
            ])
        ])
    ],
    parse(preprocess("[ a b c ] [a b [c d]]"))
)

test(
    "crazy whitespace",
    [
        Cycle([
            Notes(["a"]),
            Notes(["b"]),
            Notes(["c"]),
        ])
    ],
    parse(preprocess(""" [ a       b c
          ] """))
)

test(
    "polyphony",
    [
        Cycle([
            Notes(["a"]),
            Notes(["b", "c", "d"]),
            Notes(["c", "e"]),
        ])
    ],
    parse(preprocess("[a b,c,d c,e]"))
)

test_raises("test open without close", parse, "[a b c")
test_raises("close without open", parse, "a b c]")
test_raises("top level without brackets", parse, "a b c")

test(
    "preprocess simple AC",
    "[a b c] [a b d]",
    preprocess("[a b <c d>]")
)

test(
    "preprocess non-nested ACs",
    "[a b c [e f]] [a b c [e g]] [a b d [e f]] [a b d [e g]]",
    preprocess("[a b <c d> [e <f g>]]")
)

test(
    "preprocess nested ACs",
    "[a b c] [a b d] [a b c] [a b e]",
    preprocess("[a b <c <d e>>]")
)

test(
    "simple generation",
    [
        (['a'], Fraction(0, 1), Fraction(1, 3)),
        (['b'], Fraction(1, 3), Fraction(2, 3)),
        (['c'], Fraction(2, 3), Fraction(1, 1))
    ],
    generate_nodes(parse(preprocess("[a b c]")))
)

test(
    "nested generation",
    [
        (['a'], Fraction(0, 1), Fraction(1, 4)),
        (['b'], Fraction(1, 4), Fraction(1, 2)),
        (['c'], Fraction(1, 2), Fraction(1, 1))
    ],
    generate_nodes(parse(preprocess("[[a b] c]")))
)


test(
    "simple alternatives",
    [
        (['a'], Fraction(0, 1), Fraction(1, 1)),
        (['b'], Fraction(1, 1), Fraction(2, 1)),
        (['c'], Fraction(2, 1), Fraction(3, 1))
    ],
    generate_nodes(parse(preprocess("<[a] [b] [c]>")))
)

# TODO: figure out what the "rules" are for these and confirm they are validated/enforced
