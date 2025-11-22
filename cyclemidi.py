from __future__ import annotations  # so that Cycles methods can return Cycles instances
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from enum import Enum, auto
from midi import Config
from typing import Any, Union
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
class Rest:
    start: Fraction
    end: Fraction


@dataclass
class TreeNode:
    children: list[Union[TreeNode | str]]


@dataclass
class Note:
    start: Fraction
    end: Fraction
    pitch: str
    velocity: int
    width: Decimal
    offset: Decimal


Voice = list[Union[Note, Rest]]
CycleString = tuple[CycleStringType, str]

###
# Note: the public interface (`Cycles`) is object-orented and "fluent" but the actual processing is done
# in a series of "pure" functions defined at the module level.
###


def tokenize(cycle_string: str) -> list[str]:
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


def parse_cycles(cycle_string: str) -> list[str]:
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
    cycle_tree = TreeNode([])

    # the top level is a list of one or more cycles that we need to split up
    # and parse into the same tree
    cycles = re.split(r"(?<=\])\s*(?=\[)", cycle_string)
    for cycle in cycles:
        tokens = tokenize(cycle)
        add_cycle_to_tree(tokens, cycle_tree)

    print(cycle_tree)

    return []


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
