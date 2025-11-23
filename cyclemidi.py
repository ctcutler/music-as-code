from __future__ import annotations  # so that Cycles methods can return Cycles instances
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from enum import Enum, auto
from typing import Any, Union, Optional
from string import whitespace
import re

from mido import MidiFile, bpm2tempo, tick2second, MidiTrack, Message, MetaMessage  # type: ignore

from midi import get_midi_note_and_velocity, play_midi, Config


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


def generate_voices(tree: TreeNode, start: Fraction, end: Fraction) -> list[Voice]:
    """
    In-order traversal of tree, generating a Note object for every
    leaf node with start and end set based on the provided start, end, and the number of
    child nodes.

    """
    voices: list[Voice] = [[]]
    child_count = len(tree.children)
    increment = Fraction((end - start) / child_count)

    for i, child in enumerate(tree.children):
        # all time ranges are start-inclusive and end-exclusive.
        child_start = i * increment
        child_end = (i + 1) * increment

        if isinstance(child, TreeNode):
            child_voices = generate_voices(child, child_start, child_end)
            # TODO add polyphony support, e.g. mismatched numbers of voices
            voices = extend_voices(voices, child_voices)
        else:
            # TODO add polyphony support
            # TODO add support for setting velocity, width, offset
            voices[0].append(Note(child_start, child_end, child))

    return voices


def parse_cycles(cycle_string: str) -> tuple[list[Voice], int]:
    expanded = expand_alternatives(cycle_string)
    cycles = split_cycles(expanded)
    cycle_tree = build_cycle_tree(cycles)
    cycle_count = len(cycle_tree.children)
    voices = generate_voices(cycle_tree, Fraction(0), Fraction(cycle_count))

    return (voices, cycle_count)


def parse_cycle_strings(cycle_strings: list[CycleString]) -> tuple[list[Voice], int]:
    voices: list[Voice] = [[]]
    base_voice_idx = 0
    max_cycle_count = 0
    for cycle_string_type, cycle_string in cycle_strings:
        if cycle_string_type == CycleStringType.STACK:
            voices.append([])
            base_voice_idx = len(voices) - 1
        elif cycle_string_type == CycleStringType.NOTES:
            # TODO: add voice merging, voice count protection
            (voices, cycle_count) = parse_cycles(cycle_string)
            max_cycle_count = max(cycle_count, max_cycle_count)

    return (voices, max_cycle_count)


def generate_midi(
    voices: list[Voice], config: Config, cycle_count: int
) -> tuple[MidiFile, int]:
    mid = MidiFile()
    channel = 0

    ticks_per_cycle = mid.ticks_per_beat * config.beats_per_measure
    tempo = bpm2tempo(config.beats_per_minute)

    for voice in voices:
        track = MidiTrack()
        track.append(MetaMessage("set_tempo", tempo=tempo))

        # it's important to remember here that note.start and note.end are
        # absolute values from the beginning of the track, measured in
        # number of cycles but the Message.time values are relative to
        # time of the previous message

        prev_note_end: float = 0  # contains _absolute_ time of prev note's note_off
        for note in voice:
            # don't update prev_note_end or append Messages for rest events
            if note.pitch is not None:
                note_duration = (note.end - note.start) * config.note_width
                midi_note, velocity = get_midi_note_and_velocity(note.pitch)
                if note.velocity is not None:
                    velocity = note.velocity
                track.append(
                    Message(
                        "note_on",
                        channel=channel,
                        note=midi_note,
                        velocity=velocity,
                        # delta from preceding note_off (or start of song)
                        time=round((note.start - prev_note_end) * ticks_per_cycle),
                    )
                )
                track.append(
                    Message(
                        "note_off",
                        channel=channel,
                        note=midi_note,
                        velocity=velocity,
                        # delta from preceding note_on
                        time=round(note_duration * ticks_per_cycle),
                    )
                )
                prev_note_end = note.start + note_duration

        mid.tracks.append(track)
        channel += 1

    mid.save(config.midi_file_name)
    total_secs = tick2second(cycle_count * ticks_per_cycle, mid.ticks_per_beat, tempo)

    return (mid, total_secs)


class Cycles:
    def __init__(self) -> None:
        self.cycle_strings: list[CycleString] = []
        self.midi_file: Optional[MidiFile] = None
        self.total_secs: int = 0
        self.config: Config = Config()

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
        (voices, cycle_count) = parse_cycle_strings(self.cycle_strings)
        (self.midi_file, self.total_secs) = generate_midi(
            voices, self.config, cycle_count
        )

        return self

    def play(self) -> Cycles:
        play_midi(self.config, self.total_secs)

        return self


def notes(cycle_string: str) -> Cycles:
    return Cycles().notes(cycle_string)


def rhythm(cycle_string: str) -> Cycles:
    return Cycles().rhythm(cycle_string)
