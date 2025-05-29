from collections import namedtuple
from dataclasses import dataclass, field
from fractions import Fraction
from math import lcm

from mido import MidiFile, bpm2tempo, tick2second, MidiTrack, Message, MetaMessage

from midi import get_midi_note_and_velocity, play_midi, Config

@dataclass
class Cycle:
    children: list

@dataclass
class Event:
    start: Fraction = -1
    end: Fraction = -1
    note: str = ""
    velocity: int = -1
    gate_length: float = -1
    nudge: float = -1

# pattern types
NOTES = "NOTES"
RHYTHM = "RHYTHM"
VELOCITY = "VELOCITY"
GATE_LENGTH = "GATE_LENGTH"
NUDGE = "NUDGE"
STACK = "STACK"

def create_event(start, end, value, pattern_type):
    if pattern_type == NOTES:
        return Event(start, end, value)
    elif pattern_type == RHYTHM:
        return Event(start, end)
    elif pattern_type == VELOCITY:
        return Event(start, end, velocity=int(value))
    elif pattern_type == GATE_LENGTH:
        return Event(start, end, gate_length=float(value))
    elif pattern_type == NUDGE:
        return Event(start, end, nudge=float(value))
    else:
        raise Exception(f"unexpected pattern type {pattern_type}")


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
                notes = literal.split(",")
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

def generate_events(cycles, pattern_type):
    """
    Generate events per voice for a list of cycles.
    """
    voices = []
    for (i, cycle) in enumerate(cycles):
        voices = merge_voice_lists(
            voices,
            generate_node_events(cycle, Fraction(i), Fraction(i+1), pattern_type)
        )

    return voices

def generate_node_events(node, start, end, pattern_type):
    """
    Generate events for a single node in the parse tree.
    """

    if isinstance(node, list):
        # assumes all lists contain strings
        # returns a 2D list because each simultaneous event gets its own voice
        return [[create_event(start, end, s, pattern_type)] for s in node]
    elif isinstance(node, Cycle):
        time_increment = (end - start) / len(node.children)
        voices = []
        for (i, child) in enumerate(node.children):
            voices = merge_voice_lists(
                voices,
                generate_node_events(
                    child,
                    start + (time_increment * i),
                    start + (time_increment * (i + 1)),
                    pattern_type
                )
            )

        return voices
    else:
        raise Exception(f"unexpected node: {node}")


def events_to_midi(events_by_voice, config, cycle_count):
    mid = MidiFile()
    channel = 0

    ticks_per_cycle = mid.ticks_per_beat * config.beats_per_measure
    tempo = bpm2tempo(config.beats_per_minute)

    for voice_events in events_by_voice:
        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=tempo))

        # it's important to remember here that event.start and event.end are 
        # absolute values from the beginning of the track, measured in
        # number of cycles but the Message.time values are relative to
        # time of the previous message

        prev_note_end = 0 # contains _absolute_ time of prev note's note_off
        for event in voice_events:

            # don't update prev_note_end or append Messages for rest events
            if event.note != "~":
                note_duration = (event.end - event.start) * config.note_width
                midi_note, velocity = get_midi_note_and_velocity(event.note)
                if event.velocity != -1:
                    velocity = event.velocity
                track.append(
                    Message(
                        'note_on',
                        channel=channel,
                        note=midi_note,
                        velocity=velocity,
                        # delta from preceding note_off (or start of song)
                        time=round((event.start - prev_note_end) * ticks_per_cycle)
                    )
                )
                track.append(
                    Message(
                        'note_off',
                        channel=channel,
                        note=midi_note,
                        velocity=velocity,
                        # delta from preceding note_on
                        time=round(note_duration * ticks_per_cycle)
                    )
                )
                prev_note_end = event.start + note_duration

        mid.tracks.append(track)
        channel += 1

    mid.save(config.midi_file_name)
    total_secs = tick2second(cycle_count * ticks_per_cycle, mid.ticks_per_beat, tempo)

    return (mid, total_secs)

def build_stack(patterns):
    """
    Splits list of patterns into a list of lists as defined by STACK elements.

    Takes: list of (pattern_type, pattern) pairs
    Returns: list of lists of (pattern_type, pattern) pairs
    """ 
    stack = []
    cur = []
    for (pattern_type, pattern) in patterns:
        if pattern_type == STACK:
            if len(cur) > 0:
                stack.append(cur)
                cur = []
        else:
            cur.append((pattern_type, pattern))

    if len(cur) > 0:
        stack.append(cur)

    return stack

def build_cycles(patterns):
    """
    Converts a list of patterns into a list of cycle lists, all the same length.

    Takes: a list of (pattern_type, pattern) pairs
    Returns: a list of (pattern_type, cycles) pairs and the common cycle count
    """
    # build cycles for each pattern
    pattern_cycles = []
    for (pattern_type, pattern) in patterns:
        if pattern_type == STACK:
            pattern_cycles.append((pattern_type, []))
        else:
            pattern_cycles.append((pattern_type, parse_mini(pattern)))

    # make cycle lists all the same length
    cycle_lengths = [
        len(cycles) for (pattern_type, cycles) in pattern_cycles if len(cycles) > 0
    ]
    cycle_count = lcm(*cycle_lengths)
    pattern_cycles_extended = []
    for (pattern_type, cycles) in pattern_cycles:
        if pattern_type == STACK:
            pattern_cycles_extended.append((pattern_type, cycles))
        else:
            extended_cycles = []
            for i in range(cycle_count // len(cycles)):
                extended_cycles.extend(cycles)

            pattern_cycles_extended.append((pattern_type, extended_cycles))

    return (pattern_cycles_extended, cycle_count)

def build_voices(pattern_cycles):
    """
    Converts cycles lists into events and voices, merging them in the process.

    Takes: a list of (pattern_type, cycles) pairs
    Returns: a list of "voices" where each voice is a list of Events
    """
    voices = []
    for (pattern_type, cycles) in pattern_cycles:
        new_voices = generate_events(cycles, pattern_type)
        if len(voices) == 0:
            voices.extend(new_voices)
        else:
            for (src_voice_index, src_voice) in enumerate(new_voices):
                if src_voice_index >= len(voices):
                    break

                dst_voice = voices[src_voice_index]
                src_i = 0
                dst_i = 0
                while src_i < len(src_voice) and dst_i < len(dst_voice):
                    src_event = src_voice[src_i]
                    dst_event = dst_voice[dst_i]

                    # src starts after dst starts: no merge, inc. dst
                    if src_event.start > dst_event.start:
                        dst_i += 1
                    # src ends before (or at) dst start: no merge, inc. src
                    elif src_event.end <= dst_event.start:
                        src_i += 1
                    # src spans dst start: merge
                    else:
                        if pattern_type == NOTES:
                            dst_event.note = src_event.note
                        elif pattern_type == VELOCITY:
                            dst_event.velocity = src_event.velocity
                        elif pattern_type == GATE_LENGTH:
                            dst_event.gate_length = src_event.gate_length
                        elif pattern_type == NUDGE:
                            dst_event.nudge = src_event.nudge
                        else:
                            raise Exception(f"unexpected pattern type {pattern_type}")

                        # always increment dst here because we've merged into it
                        dst_i += 1

    return voices

def notes(mini_string):
    return Mini().notes(mini_string)

class Mini:

    def __init__(self, patterns=None):
        self.patterns = patterns if patterns else []
        self.midi_file = None
        self.total_secs = None
        self.config = Config()

    def notes(self, mini_string):
        self.patterns.append((NOTES, mini_string))
        return self

    def rhythm(self, mini_string):
        self.patterns.append((RHYTHM, mini_string))
        return self

    def velocity(self, mini_string):
        self.patterns.append((VELOCITY, mini_string))
        return self

    def gate_length(self, mini_string):
        self.patterns.append((GATE_LENGTH, mini_string))
        return self

    def nudge(self, mini_string):
        self.patterns.append((NUDGE, mini_string))
        return self

    def stack(self):
        self.patterns.append((STACK, ""))
        return self

    def set_config(self, param, val):
        setattr(self.config, param, val)
        return self

    def midi(self):
        """
        How this works generally:
        - we build a "stack" of groups of patterns that are meant to play
          simultaneously
        - for every pattern group we:
          - build cycles from the individual patterns
          - merge the cycles and build lists of events (one per simultaneous voice)
        - create MIDI messages from the per-voice events
        """
        stack = build_stack(self.patterns)
        voices = []
        max_cycle_count = 0
        for patterns in stack:
            (pattern_cycles, cycle_count) = build_cycles(patterns)
            max_cycle_count = max(cycle_count, max_cycle_count)
            pattern_voices = build_voices(pattern_cycles)
            voices.extend(pattern_voices)

        (self.midi_file, self.total_secs) = events_to_midi(voices, self.config, cycle_count)

        return self

    def play(self):
        play_midi(self.config, self.total_secs)
