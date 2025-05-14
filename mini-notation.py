class Node:
    def __init__(self, children=None):
        self.children = children or []

    def __eq__(self, other):
        return self.children == other.children

class DividedCycle(Node):
    def __repr__(self):
        return "DividedCycle: " + repr(self.children)

class AlternativeCycle(Node):
    def __repr__(self):
        return "AlternativeCycle: " + repr(self.children)

class Notes(Node):
    def __init__(self, notes=None):
        super().__init__()
        self.notes = notes or []

    def __eq__(self, other):
        if not isinstance(other, Notes):
            return False
        return self.notes == other.notes and super().__eq__(other)

    def __repr__(self):
        return repr(self.notes)

def parse(s):
    cur_node = AlternativeCycle()
    stack = []
    literal = ""

    for c in s:
        if c in {"[", "<"}:
            stack.append(cur_node)
            if c == "[":
                cur_node = DividedCycle()
            else:
                cur_node = AlternativeCycle()
        elif c in {" ", "\n", "\t", "]", ">"}:
            if literal:
                cur_node.children.append(Notes(literal.split(",")))
            literal = ""
            if c in {"]", ">"}:
                if not stack:
                    raise Exception(f"Unbalanced brackets in {s}")

                if isinstance(cur_node, AlternativeCycle) and c == "]":
                    raise Exception(f"Unbalanced brackets in {s}")

                if isinstance(cur_node, DividedCycle) and c == ">":
                    raise Exception(f"Unbalanced brackets in {s}")

                stack[-1].children.append(cur_node)
                cur_node = stack.pop()
        else:
            literal += c

    if literal:
        cur_node.children.append(Notes(literal.split(",")))

    if stack:
        raise Exception(f"Unbalanced brackets in {s}")

    return cur_node

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
    "one level, divided cycle",
    AlternativeCycle([
        DividedCycle([
            Notes(["a"]),
            Notes(["b"]),
            Notes(["c"]),
        ])
    ]),
    parse("[a b c]")
)

test(
    "one level, alternative cycle",
    AlternativeCycle([
        Notes(["a"]),
        Notes(["b"]),
        Notes(["c"]),
    ]),
    parse("a b c")
)

test(
    "two levels of alternative cycles",
    AlternativeCycle([
        AlternativeCycle([
            Notes(["a"]),
            Notes(["b"]),
            Notes(["c"]),
        ])
    ]),
    parse("<a b c>")
)


test(
    "three level nesting",
    AlternativeCycle([
        DividedCycle([
            Notes(["a"]), 
            Notes(["b"]),
            Notes(["c"])
        ]),
        DividedCycle([
            Notes(["a"]),
            Notes(["b"]),
            DividedCycle([
                Notes(["c"]), 
                Notes(["d"])
            ])
        ])
    ]),
    parse("[ a b c ] [a b [c d]]")
)
test(
    "crazy whitespace",
    AlternativeCycle([
        DividedCycle([
            Notes(["a"]),
            Notes(["b"]),
            Notes(["c"]),
        ])
    ]),
    parse(""" [ a       b c
          ] """)
)

test(
    "polyphony",
    AlternativeCycle([
        DividedCycle([
            Notes(["a"]),
            Notes(["b", "c", "d"]),
            Notes(["c", "e"]),
        ])
    ]),
    parse("[a b,c,d c,e]")
)

test_raises("test open without close", parse, "a b c]")
test_raises("close without open", parse, "a b c]")
test_raises("mixed bracket types", parse, "[a b c>")

