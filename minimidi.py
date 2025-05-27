from collections import namedtuple
from fractions import Fraction

from mido import MidiFile, bpm2tempo, tick2second, MidiTrack, Message, MetaMessage

from midi import get_midi_note_and_velocity, play_midi, Config

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


def mini_to_midi(mini_notations, config):
    """
    Converts mini notation string to MIDI.

    Future design: takes multiple "layers" where each layer has a pattern
    and corresponds to a parameter (pitch, velocity, midi "MOD", 
    midi "aftertouch" "portamento" etc.).  The order of the 
    patterns determines which pattern takes precedent.  

    TODO
    - stack rhythm patterns (e.g. one voice holds a note while another plays two)
    - live update
    - handle layers
    - handle swing
    """
    if isinstance(mini_notations, str):
        mini_notations = [mini_notations]

    mid = MidiFile()
    channel = 0

    ticks_per_cycle = mid.ticks_per_beat * config.beats_per_measure
    tempo = bpm2tempo(config.beats_per_minute)

    for mini in mini_notations:
        cycles = parse_mini(mini)
        events_by_voice = generate_events(cycles)

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
                if event.value != "~":
                    note_duration = (event.end - event.start) * config.note_width
                    midi_note, velocity = get_midi_note_and_velocity(event.value)
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

    return (mid, tick2second(len(cycles) * ticks_per_cycle, mid.ticks_per_beat, tempo))

def notes(mini_string):
    return Mini().notes(mini_string)

class Mini:
    NOTES = "NOTES"
    RHYTHM = "RHYTHM"
    VELOCITY = "VELOCITY"
    GATE_LENGTH = "GATE_LENGTH"
    NUDGE = "NUDGE"

    def __init__(self, patterns=None):
        self.patterns = patterns if patterns else []
        self.midi_file = None
        self.total_secs = None
        self.config = Config()

    def notes(self, mini_string):
        self.patterns.append((self.NOTES, mini_string))
        return self

    def rhythm(self, mini_string):
        self.patterns.append((self.RHYTHM, mini_string))
        return self

    def velocity(self, mini_string):
        self.patterns.append((self.VELOCITY, mini_string))
        return self

    def gate_length(self, mini_string):
        self.patterns.append((self.GATE_LENGTH, mini_string))
        return self

    def nudge(self, mini_string):
        self.patterns.append((self.NUDGE, mini_string))
        return self

    def set_config(self, param, val):
        setattr(self.config, param, val)
        return self

    def midi(self):
        # TODO: this is a first pass, each successive pattern overwrites
        # the previous, # pattern type is ignored, treating everything as
        # a NOTES pattern
        for (pattern_type, pattern) in self.patterns:
            (self.midi_file, self.total_secs) = mini_to_midi(pattern, self.config)

        return self

    def play(self):
        play_midi(config, self.total_secs)
