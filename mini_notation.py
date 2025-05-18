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

