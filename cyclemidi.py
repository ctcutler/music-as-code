from __future__ import annotations  # so that Cycles methods can return Cycles instances
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from enum import Enum, auto
from midi import Config
from typing import Any, Union, Optional
from string import whitespace
import re


class CycleStringType(Enum):
    NOTES = auto()
    RHYTHM = auto()
    VELOCITY = auto()
    GATE_LENGTH = auto()
    NUDGE = auto()
    STACK = auto()


@dataclass
class TreeNode:
    children: list[Union[TreeNode | str]]


@dataclass
class Note:
    start: Fraction
    end: Fraction
    pitch: Optional[str] = None
    velocity: Optional[int] = None
    width: Optional[Decimal] = None
    offset: Optional[Decimal] = None


Voice = list[Note]
CycleString = tuple[CycleStringType, str]

###
# Note: the public interface (`Cycles`) is object-orented and "fluent" but the actual processing is done
# in a series of "pure" functions defined at the module level.
###


def tokenize(cycle_string: str) -> list[str]:
    """
    Tokenizes a cycle string into "[", "]", and continguous non-whitespace tokens.
    """
    tokens = []
    cur_token = ""
    for c in cycle_string:
        if c not in whitespace + "[]":
            cur_token += c
        else:
            if cur_token != "":
                tokens.append(cur_token)
                cur_token = ""
            if c in "[]":
                tokens.append(c)

    if cur_token != "":
        tokens.append(cur_token)

    return tokens


def expand_alternatives(s: str) -> str:
    """
    Recursively expands out all alternative cycles by making copies of the whole string
    starting with the most deeply nested alternative cycles.
    """
    start = None
    end = None

    # find the first complete angle bracket pair, a.k.a. the first one that doesn't
    # have another nested within it
    for i, c in enumerate(s):
        if c == "<":
            start = i
        elif c == ">":
            end = i + 1
            break

    if start is not None and end is not None:
        alternative_cycle = s[start:end]
        cycle_elements = alternative_cycle.strip("<>").split(" ")
        copies = [
            expand_alternatives(f"{s[:start]}{element}{s[end:]}")
            for element in cycle_elements
        ]
        return " ".join(copies)
    else:
        return s


def add_cycle_to_tree(tokens: list[str], tree: TreeNode) -> int:
    """
    Adds the tokens of a single (potentially nested) cycle into an
    existing tree.
    """
    i = 0
    token_count = len(tokens)
    while i < token_count:
        token = tokens[i]
        if token == "[":  # this is subtree's open brackent
            subtree = TreeNode([])
            tokens_consumed = add_cycle_to_tree(tokens[i + 1 :], subtree)
            tree.children.append(subtree)
            i += tokens_consumed + 1
        elif token == "]":  # this  is tree's close bracket
            return i
        else:
            tree.children.append(token)
            i += 1

    raise Exception(f"{tokens} has mismatched brackets")


def split_cycles(cycle_string: str) -> list[str]:
    """
    The top level cycle string is a list of one or more cycles that we need to split up
    and parse into the same tree.

    Lookahead and lookbehind groups ensure we preserve the brackets even while splitting
    on them.
    """
    return re.split(r"(?<=\])\s*(?=\[)", cycle_string)


def build_cycle_tree(cycles: list[str]) -> TreeNode:
    cycle_tree = TreeNode([])

    for cycle in cycles:
        tokens = tokenize(cycle)
        add_cycle_to_tree(tokens, cycle_tree)

    return cycle_tree


def z(L: list[Any]) -> list[Any]:
    """
    Helper that avoids repeating list(zip(*some_list)) a billion times.
    """
    return [list(x) for x in zip(*L)]


def extend_voices(L: list[Voice], R: list[Voice]) -> list[Voice]:
    return z(z(L) + z(R))


def generate_notes(tree: TreeNode, start: Fraction, end: Fraction) -> list[Voice]:
    """
    In-order traversal of tree, generating a Note object for every
    leaf node with start and end set based on the provided start, end, and the number of
    child nodes.

    """
    voices: list[Voice] = [[]]
    child_count = len(tree.children)
    increment = Fraction((end - start) / child_count)

    print(tree)
    for i, child in enumerate(tree.children):
        # all time ranges are start-inclusive and end-exclusive.
        child_start = i * increment
        child_end = (i + 1) * increment

        if isinstance(child, TreeNode):
            child_voices = generate_notes(child, child_start, child_end)
            # TODO add polyphony support, e.g. mismatched numbers of voices
            voices = extend_voices(voices, child_voices)
        else:
            # TODO add polyphony support
            voices[0].append(Note(child_start, child_end))

    return voices


def parse_cycles(cycle_string: str) -> list[Voice]:
    """
    So:
    - treeify
    - count elements at current level
    - for each element at current level:
      - if leaf:
        set length
      - if node:
        recurse
    """
    expanded = expand_alternatives(cycle_string)
    cycles = split_cycles(expanded)
    cycle_tree = build_cycle_tree(cycles)
    notes = generate_notes(cycle_tree, Fraction(0), Fraction(len(cycle_tree.children)))

    print(notes)

    return notes


def parse_cycle_strings(cycle_strings: list[CycleString]) -> list[Voice]:
    voices: list[Voice] = [[]]
    base_voice_idx = 0
    for cycle_string_type, cycle_string in cycle_strings:
        if cycle_string_type == CycleStringType.STACK:
            voices.append([])
            base_voice_idx = len(voices) - 1
        elif cycle_string_type == CycleStringType.NOTES:
            parse_cycles(cycle_string)
            # split cycles into notes
            # append notes to voice(s)

    return voices


def generate_midi(voices: list[Voice]) -> None:
    pass


class Cycles:
    def __init__(self) -> None:
        self.cycle_strings: list[CycleString] = []
        self.midi_file = None
        self.total_secs = None
        self.config = Config()

    # "public" methods
    def notes(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.NOTES, cycle_string))
        return self

    def rhythm(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.RHYTHM, cycle_string))
        return self

    def velocity(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.VELOCITY, cycle_string))
        return self

    def gate_length(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.GATE_LENGTH, cycle_string))
        return self

    def nudge(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.NUDGE, cycle_string))
        return self

    def stack(self) -> Cycles:
        self.cycle_strings.append((CycleStringType.STACK, ""))
        return self

    def set_config(self, param: str, val: Any) -> Cycles:
        setattr(self.config, param, val)
        return self

    def midi(self) -> Cycles:
        voices = parse_cycle_strings(self.cycle_strings)
        generate_midi(voices)

        return self

    def play(self) -> Cycles:
        # play_midi(self.config, self.total_secs)

        return self


def notes(cycle_string: str) -> Cycles:
    return Cycles().notes(cycle_string)


def rhythm(cycle_string: str) -> Cycles:
    return Cycles().rhythm(cycle_string)
