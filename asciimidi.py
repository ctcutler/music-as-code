from collections import namedtuple
import re
import sys

from mido import MidiFile, MidiTrack, Message, MetaMessage, open_output, Backend, bpm2tempo

ASCII_NOTE_RE = re.compile('(\D+)(\d+)(\+*)(\-*)')
WS_RE = re.compile(' +')

CONFIG_FIELD_DEFAULTS = {
    "beats_per_minute": 120,
    "symbols_per_beat": 2,
    "note_width": .5,          
    "swing": .5,               
    "midi_device": "FH-2", # Or 'Elektron Model:Cycles' or 'IAC Driver Bus 1'     
    "midi_file_name": "new_song.mid",
    "midi_backend": "mido.backends.portmidi",
    "loops": 1,
    # "beats_per_measure": 4, # haven't found a reason we need this yet
}
Config = namedtuple(
    'Config', 
    CONFIG_FIELD_DEFAULTS.keys(), 
    defaults=CONFIG_FIELD_DEFAULTS.values()
)

midi_note_numbers = {
  'R': 0, 
  'C': 24, 
  'C#': 25,
  'Db': 25,
  'D': 26, 
  'D#': 27,
  'Eb': 27,
  'E': 28, 
  'F': 29,
  'F#': 30,
  'Gb': 30,
  'G': 31, 
  'G#': 32,
  'Ab': 32,
  'A': 33, 
  'A#': 34,
  'Bb': 34,
  'B': 35, 
}

def get_midi_note(note, octave):
    return midi_note_numbers[note] + (int(octave) * 12)

rest_length = 0
def process_symbol(track, channel, symbol, symbol_start, symbol_end):
    global rest_length
    if symbol in ('---', '--'):
        rest_length += symbol_start + symbol_end
    else:
        if symbol in ('===', '=='):
            track[-1].time += symbol_start + symbol_end
        else: 
            m = ASCII_NOTE_RE.search(symbol)
            symbol, octave, up_volume, down_volume = m.groups()
            midi_note = get_midi_note(symbol, octave)
            velocity = 60 
            velocity += 20 * len(up_volume) 
            velocity -= 20 * len(down_volume) 

            track.append(
                Message(
                    'note_on',
                    channel=channel,
                    note=midi_note,
                    velocity=velocity,
                    # delta from preceding note_off (or start of song)
                    time=rest_length+symbol_start
                )
            )
            track.append(
                Message(
                    'note_off',
                    channel=channel,
                    note=midi_note,
                    velocity=velocity,
                    # delta from preceding note_on
                    time=symbol_end
                )
            )

        rest_length = 0

def ascii_to_midi(asciis, config):
    "Assumes asciis is a list of strings and each has same number of newlines"""
    mid = MidiFile()
    channel = 0
    ticks_per_symbol = mid.ticks_per_beat // config.symbols_per_beat
    ticks_per_pair = 2 * ticks_per_symbol
    global rest_length

    # if single str, wrap in list
    if isinstance(asciis, str):
        asciis = [asciis]

    split_by_newline = [a.split('\n') for a in asciis]
    zipped = zip(*split_by_newline)
    music = '\n'.join([' '.join(z) for z in zipped])

    left_swing = config.swing * ticks_per_pair
    right_swing = (1 - config.swing) * ticks_per_pair
    left_end = right_end = int(config.note_width * right_swing)
    left_start = int(right_swing - right_end)
    right_start = int(left_swing - left_end)

    # reversed() so that the "bottom" voice is channel 0
    for voice in reversed(music.strip().split('\n')):
        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(config.beats_per_minute)))
        symbols = WS_RE.split(voice.strip())
        symbol_pairs = zip(symbols[0::2], symbols[1::2])

        is_first_pair = True
        for (left, right) in symbol_pairs:
            process_symbol(track, channel, left, 0 if is_first_pair else left_start, left_end)
            process_symbol(track, channel, right, right_start, right_end)
            is_first_pair = False

        mid.tracks.append(track)
        channel += 1
        rest_length = 0

    mid.save(config.midi_file_name)

    return mid

def print_ascii(asciis):
    for a in asciis:
        print(a)
        print()

def play(asciis, config):
    print_ascii(asciis)
    ascii_to_midi(asciis, config)

    # user may pass None 
    if not config.midi_device:
        return 

    portmidi = Backend(config.midi_backend)
    for i in range(config.loops):
        with portmidi.open_output(config.midi_device) as midi_port:
            try:
                for msg in MidiFile(config.midi_file_name).play():
                    midi_port.send(msg)
            except KeyboardInterrupt:
                midi_port.reset()
                sys.exit(1)

def stack(layers):
    return "\n".join(layers)

def concat(measures):
    layers = zip(*[measure.split("\n") for measure in measures])
    return stack("   ".join(layer) for layer in layers)

def key_pitches(key_root, mode, semis):
    pitches = SHARP_PITCHES if f"{key_root} {mode}" in SHARPS_KEYS else FLAT_PITCHES
    root_index = pitches.index(key_root)
    pitches_for_key = [ pitches[(root_index + i) % 12] for i in semis ]

    # rotate list of pitches so they start with C/C#/Db to simplify octave shift calculations
    if "C" in pitches_for_key:
        start_index = pitches_for_key.index("C")
    elif "C#" in pitches_for_key:
        start_index = pitches_for_key.index("C#")
    else:
        assert "Db" in pitches_for_key
        start_index = pitches_for_key.index("Db")

    return pitches_for_key[start_index:] + pitches_for_key[:start_index]

MAJOR_SEMIS = [ 0, 2, 4, 5, 7, 9, 11 ]
MINOR_SEMIS = [ 0, 2, 3, 5, 7, 8, 10 ]
SHARP_PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_PITCHES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# according to https://en.wikipedia.org/wiki/Circle_of_fifths
MAJOR_KEYS = [ "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" ]
MINOR_KEYS = [ "C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B" ]

# keys traditionally expressed with sharps, all other keys assumed to be expresed with flats
SHARPS_KEYS = { "G major", "D major", "A major", "E major", "B major", "E minor", "B minor",
    "F# minor", "C# minor", "G# minor" }

# weird ** syntax combines two dicts
KEYS = {
    **{f"{key_root} major": key_pitches(key_root, "major", MAJOR_SEMIS) for key_root in MAJOR_KEYS},
    **{f"{key_root} minor": key_pitches(key_root, "minor", MINOR_SEMIS) for key_root in MINOR_KEYS}
}

# mapped to in-key steps
IN_KEY_INTERVALS = {
    "2nd": 1,
    "3rd": 2,
    "4th": 3,
    "5th": 4,
    "6th": 5,
    "7th": 6,
    "8th": 7
}

# maps to semitones
FIXED_INTERVALS = {
    "m2": 1,
    "M2": 2,
    "m3": 3,
    "M3": 4,
    "P4": 5,
    "TT": 6,
    "P5": 7,
    "m6": 8,
    "M6": 9,
    "m7": 10,
    "M7": 11,
}

global_key = None
def set_key(key):
    global global_key
    root, mode = key.split()
    assert root[0] in ("A", "B", "C", "D", "E", "F", "G")
    assert len(root) < 3
    if len(root) > 1: 
        assert root[1] in ("#", "b")
    assert mode.startswith("maj") or mode.startswith("min")
    global_key = key

class Note:
    def __init__(self, s, key=None):
        m = ASCII_NOTE_RE.search(s)
        self.pitch, self.octave, self.up_volume, self.down_volume = m.groups()
        self.octave = int(self.octave)
        if key:
            set_key(key)
        else:
            key = global_key
        assert key
        self.key = key

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __str__(self):
        return self.pitch+str(self.octave)+self.up_volume+self.down_volume

    def __add__(self, other):
        if isinstance(other, int):
            return add_scale_steps(self, other, self.key)
        elif other in IN_KEY_INTERVALS:
            return add_scale_steps(self, IN_KEY_INTERVALS[other], self.key)
        elif other in FIXED_INTERVALS:
            return add_semitones(self, FIXED_INTERVALS[other])
        else:
            raise Exception(f"unexpected addend: {other}")

    def __sub__(self, other):
        if isinstance(other, int):
            return add_scale_steps(self, -other, self.key)
        elif other in IN_KEY_INTERVALS:
            return add_scale_steps(self, -IN_KEY_INTERVALS[other], self.key)
        elif other in FIXED_INTERVALS:
            return add_semitones(self, -FIXED_INTERVALS[other])
        else:
            raise Exception(f"unexpected subtrahend: {other}")

def n(s, key=None):
    return Note(s, key)

def add_semitones(note, semitones):
    pitch, octave = note.pitch, note.octave
    pitches = FLAT_PITCHES if pitch[-1] == "b" else SHARP_PITCHES
    i = pitches.index(pitch)
    i += semitones
    octave += i // len(pitches)
    pitch = pitches[i % len(pitches)]

    return n(pitch+str(octave))

def add_scale_steps(note, scale_steps, key=None):
    """
    Takes a note, a number of scale steps, and key and returns a new note that is that
    many steps away in that key.
    """
    if key:
        set_key(key)
    else:
        key = global_key
    assert key
    key_pitches = KEYS[key]

    # note: this only works because we rotate all key pitch lists to start with C/C#/Db
    note_index = key_pitches.index(note.pitch) + (7 * note.octave)
    new_index = note_index + scale_steps
    new_pitch = key_pitches[new_index % 7]
    new_octave = new_index // 7

    return n(new_pitch+str(new_octave))
    
# FIXME: move a bunch of this stuff to utils?
