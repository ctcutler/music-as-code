from collections import namedtuple
from dataclasses import dataclass, field
from fractions import Fraction

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
        return Event(start, end, velocity=value)
    elif pattern_type == GATE_LENGTH:
        return Event(start, end, gate_length=value)
    elif pattern_type == NUDGE:
        return Event(start, end, nudge=value)
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


def events_to_midi(events_by_voice, config):
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
    total_secs = tick2second(len(events_by_voice[0]) * ticks_per_cycle, mid.ticks_per_beat, tempo)

    return (mid, total_secs)

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
        for each pattern:
            first, converts a list of (pattern_type, pattern) pairs into a
            2D list of events where the first dimension is "voice" and the
            second is events in each voice

            second, merges the new pattern's voices into a list of "already
            merged" voices according to the following rules:
            - if RH (merging in) starts before or at the same time as LH
              (already merged) and ends after LH started, RH's value
              (note, velocity, etc. per the pattern type) overwrites LH's
            - if LH is empty, RH is copied directly to it
            - if LH and RH are not the same number of cycles, they are duplicated
              into the shortest sequence allows for even repeats of both
              sequences of cycles, e.g.: two cycle sequence A B combines with 
              three cycle sequence C D E into six cycle sequence: A/C B/D A/E B/C A/D B/E
            - where LH and RH have different numbers of voices, additional
              event-less "silent" voices are added

            special case: when a STACK pattern_type is encountered, all
            previous voices are frozen and we start with new ones

        once merging is complete, convert the list of voices into a MidiFile 
        with one track and one channel per voice and a list of messages built
        from those events
        """
        voices = [[]]
        mergeable_voices = 0 # all voices at/after this index are available for merging
        for (pattern_type, pattern) in self.patterns:
            if pattern_type == STACK:
                voices.append([])
                mergeable_voices = len(voices) - 1 
                continue

            # make pattern events
            cycles = parse_mini(pattern)

            # merge into existing message lists (not yet, overwriting instead, for now)
            voices = generate_events(cycles, pattern_type)

        (self.midi_file, self.total_secs) = events_to_midi(voices, self.config)

        return self

    def play(self):
        play_midi(config, self.total_secs)
