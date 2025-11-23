from __future__ import annotations  # so that Cycles methods can return Cycles instances
from dataclasses import dataclass, replace
from decimal import Decimal
from fractions import Fraction
from enum import Enum, auto
from typing import Any, Union, Optional
from string import whitespace
from math import lcm, floor
import re

from mido import MidiFile, bpm2tempo, tick2second, MidiTrack, Message, MetaMessage  # type: ignore

from midi import get_midi_note_and_velocity, play_midi, Config


class CycleListType(Enum):
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
    pitch: str = ""
    velocity: Optional[int] = None
    width: Optional[Decimal] = None
    offset: Optional[Decimal] = None


Voice = list[Note]
CycleList = tuple[CycleListType, str]

###
# Note: the public interface (`Cycles`) is object-orented and "fluent" but the actual processing is done
# in a series of "pure" functions defined at the module level.
###


def tokenize(cycle_list: str) -> list[str]:
    """
    Tokenizes a cycle list into "[", "]", and continguous non-whitespace tokens.
    """
    tokens = []
    cur_token = ""
    for c in cycle_list:
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


def split_cycles(cycle_list: str) -> list[str]:
    """
    The top level cycle list is a list of one or more cycles that we need to split up
    and parse into the same tree.

    Lookahead and lookbehind groups ensure we preserve the brackets even while splitting
    on them.
    """
    return re.split(r"(?<=\])\s*(?=\[)", cycle_list)


def build_cycle_tree(cycles: list[str]) -> TreeNode:
    cycle_tree = TreeNode([])

    for cycle in cycles:
        tokens = tokenize(cycle)
        add_cycle_to_tree(tokens, cycle_tree)

    return cycle_tree


def normalize_voice_counts(
    left: list[Voice], right: list[Voice]
) -> tuple[list[Voice], list[Voice]]:
    left_len = len(left)
    right_len = len(right)
    max_voice_count = max(left_len, right_len)
    new_left = []
    new_right = []
    for i in range(max_voice_count):
        new_left.append([] if i >= left_len else left[i])
        new_right.append([] if i >= right_len else right[i])

    return (new_left, new_right)


def extend_voices(left: list[Voice], right: list[Voice]) -> list[Voice]:
    (left, right) = normalize_voice_counts(left, right)
    assert len(left) == len(right)
    return [left[i] + right[i] for i in range(len(left))]


def calc_voice_lengths(voices: list[Voice]) -> list[int]:
    """
    Takes a list of voices (potentially) containing different numbers of cycles.
    Uses the fact that the start and end values of Notes are Fractions of cycle
    counts to determine how long (in cycles) each voice is.
    """
    voice_lengths = []
    for voice in voices:
        assert len(voice) > 0  # we don't expect any empty voices

        note = voice[-1]
        idx = floor(note.end)

        # Our method gets the index of the last cycle so normally we have to
        # add one to get the count of cycles.  However, if the end of the last
        # note coincides with a cycle boundary, it will be an integer that is
        # the index of the *next* cycle so no need to add one.
        if note.end.denominator == 1:
            voice_lengths.append(idx)
        else:
            voice_lengths.append(idx + 1)

    return voice_lengths


def calc_desired_voice_length(voices: list[Voice]) -> int:
    """
    Uses the results of calc_voice_lengths to figure out how to evenly
    multiply the shorter ones out until they are all the same length.
    """
    voice_lengths = calc_voice_lengths(voices)
    return lcm(*voice_lengths)


def normalize_voice_length(
    voices: list[Voice], desired_voice_length: int
) -> list[Voice]:
    voice_lengths = calc_voice_lengths(voices)

    new_voices = []
    for i, voice in enumerate(voices):
        new_voice = []
        for j in range(desired_voice_length // voice_lengths[i]):
            offset = j * voice_lengths[i]
            for note in voice:
                new_voice.append(
                    replace(note, start=note.start + offset, end=note.end + offset)
                )
        new_voices.append(new_voice)

    return new_voices


def generate_voices(
    tree: TreeNode, start: Fraction, end: Fraction, cycle_list_type: CycleListType
) -> list[Voice]:
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
        child_start = start + (i * increment)
        child_end = start + ((i + 1) * increment)

        if isinstance(child, TreeNode):
            child_voices = generate_voices(
                child, child_start, child_end, cycle_list_type
            )
            voices = extend_voices(voices, child_voices)
        else:
            # TODO add support for setting width, offset
            note_values = child.split(",")
            missing_voice_count = len(note_values) - len(voices)
            if missing_voice_count > 0:
                for i in range(missing_voice_count):
                    voices.append([])
            for i, note_value in enumerate(note_values):
                note = Note(child_start, child_end)
                if cycle_list_type == CycleListType.NOTES:
                    note.pitch = note_value
                elif cycle_list_type == CycleListType.RHYTHM:
                    pass  # start and end are already set
                elif cycle_list_type == CycleListType.VELOCITY:
                    velocity = int(note_value)
                    assert velocity >= 0 and velocity <= 9
                    note.velocity = int((velocity / 9) * 127)
                voices[i].append(note)

    return voices


def merge_note(
    left_note: Note, right_note: Note, cycle_list_type: CycleListType
) -> Note:
    # TODO add other cycle list types
    if cycle_list_type == CycleListType.VELOCITY:
        assert left_note.velocity is None
        return replace(left_note, velocity=right_note.velocity)
    elif cycle_list_type == CycleListType.NOTES:
        assert left_note.pitch == ""
        return replace(left_note, pitch=right_note.pitch)

    raise Exception(f"Unexpected cycle list type: {cycle_list_type}")


def merge_voice(
    left_voice: Voice, right_voice: Voice, cycle_list_type: CycleListType
) -> Voice:
    # we should only get here if there's something to merge into
    assert len(left_voice) > 0

    # merging rhythm into anything else is not supported, it must come first
    assert cycle_list_type != CycleListType.RHYTHM

    right_i = 0
    left_i = 0
    new_voice = []
    while right_i < len(right_voice) and left_i < len(left_voice):
        right_note = right_voice[right_i]
        left_note = left_voice[left_i]

        # right starts after left starts: no merge, inc. left
        if right_note.start > left_note.start:
            left_i += 1
        # right ends before (or at) left start: no merge, inc. right
        elif right_note.end <= left_note.start:
            right_i += 1
        # right spans left start: merge
        else:
            new_note = merge_note(left_note, right_note, cycle_list_type)
            new_voice.append(new_note)

            # always increment left here because we've merged into it
            left_i += 1

    return new_voice


def parse_cycles(
    cycle_list: str, cycle_list_type: CycleListType
) -> tuple[list[Voice], int]:
    expanded = expand_alternatives(cycle_list)
    cycles = split_cycles(expanded)
    cycle_tree = build_cycle_tree(cycles)
    cycle_count = len(cycle_tree.children)
    voices = generate_voices(
        cycle_tree, Fraction(0), Fraction(cycle_count), cycle_list_type
    )

    return (voices, cycle_count)


def parse_cycle_lists(cycle_lists: list[CycleList]) -> tuple[list[Voice], int]:
    voices: list[Voice] = [[]]
    base_voice_idx = 0
    max_cycle_count = 0
    for cycle_list_type, cycle_list in cycle_lists:
        if cycle_list_type == CycleListType.STACK:
            voices.append([])
            base_voice_idx = len(voices) - 1
        else:
            (new_voices, cycle_count) = parse_cycles(cycle_list, cycle_list_type)
            existing_voices = voices[base_voice_idx:]
            if existing_voices == [[]]:  # nothing to merge into
                voices[base_voice_idx:] = new_voices
            else:
                (existing_voices, new_voices) = normalize_voice_counts(
                    existing_voices, new_voices
                )
                assert len(existing_voices) == len(new_voices)
                desired_voice_length = calc_desired_voice_length(
                    existing_voices + new_voices
                )
                existing_voices = normalize_voice_length(
                    existing_voices, desired_voice_length
                )
                new_voices = normalize_voice_length(new_voices, desired_voice_length)
                merged_voices = [
                    merge_voice(existing_voices[i], new_voices[i], cycle_list_type)
                    for i in range(len(new_voices))
                ]
                voices[base_voice_idx:] = merged_voices
            max_cycle_count = max(cycle_count, max_cycle_count)

    desired_voice_length = calc_desired_voice_length(voices)
    voices = normalize_voice_length(voices, desired_voice_length)

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
            if note.pitch != "~":
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
        self.cycle_lists: list[CycleList] = []
        self.midi_file: Optional[MidiFile] = None
        self.total_secs: int = 0
        self.config: Config = Config()

    # "public" methods
    def notes(self, cycle_list: str) -> Cycles:
        self.cycle_lists.append((CycleListType.NOTES, cycle_list))
        return self

    def rhythm(self, cycle_list: str) -> Cycles:
        self.cycle_lists.append((CycleListType.RHYTHM, cycle_list))
        return self

    def velocity(self, cycle_list: str) -> Cycles:
        self.cycle_lists.append((CycleListType.VELOCITY, cycle_list))
        return self

    def gate_length(self, cycle_list: str) -> Cycles:
        self.cycle_lists.append((CycleListType.GATE_LENGTH, cycle_list))
        return self

    def nudge(self, cycle_list: str) -> Cycles:
        self.cycle_lists.append((CycleListType.NUDGE, cycle_list))
        return self

    def stack(self) -> Cycles:
        self.cycle_lists.append((CycleListType.STACK, ""))
        return self

    def set_config(self, param: str, val: Any) -> Cycles:
        setattr(self.config, param, val)
        return self

    def midi(self) -> Cycles:
        (voices, cycle_count) = parse_cycle_lists(self.cycle_lists)
        (self.midi_file, self.total_secs) = generate_midi(
            voices, self.config, cycle_count
        )

        return self

    def play(self) -> Cycles:
        play_midi(self.config, self.total_secs)

        return self


def notes(cycle_list: str) -> Cycles:
    return Cycles().notes(cycle_list)


def rhythm(cycle_list: str) -> Cycles:
    return Cycles().rhythm(cycle_list)
