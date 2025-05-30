from types import GeneratorType

from midi import ASCII_NOTE_RE

def handle_mixed_args(args):
    result = []
    for arg in args:
        if isinstance(arg, list) or isinstance(arg, tuple) or isinstance(arg, GeneratorType):
            result += arg
        else:
            result.append(arg)
    return result

def stack(*args):
    layers = handle_mixed_args(args)
    return "\n".join(layer.strip("\n") for layer in layers)

def concat(*args):
    measures = handle_mixed_args(args)
    layers = zip(*[measure.split("\n") for measure in measures])
    return stack("   ".join(layer) for layer in layers)

def print_ascii(asciis):
    for a in asciis:
        print(a)
        print()

def make_lines(*args):
    bars = handle_mixed_args(args)
    return [
        concat(bars[i:i+2]) for i in range(0, len(bars), 2)
    ]

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
PHRYGIAN_SEMIS = [ 0, 1, 3, 5, 7, 8, 10 ]
SHARP_PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_PITCHES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# according to https://en.wikipedia.org/wiki/Circle_of_fifths
MAJOR_KEYS = [ "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" ]
MINOR_KEYS = [ "C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B" ]
# no idea what's "correct" but this appears to work
PHRYGIAN_KEYS = [ "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" ]

# keys traditionally expressed with sharps, all other keys assumed to be expresed with flats
SHARPS_KEYS = { "G major", "D major", "A major", "E major", "B major", "E minor", "B minor",
    "F# minor", "C# minor", "G# minor" }

# weird ** syntax combines two dicts
KEYS = {
    **{f"{key_root} major": key_pitches(key_root, "major", MAJOR_SEMIS) for key_root in MAJOR_KEYS},
    **{f"{key_root} minor": key_pitches(key_root, "minor", MINOR_SEMIS) for key_root in MINOR_KEYS},
    **{f"{key_root} phrygian": key_pitches(key_root, "phrygian", PHRYGIAN_SEMIS) for key_root in PHRYGIAN_KEYS}
}

oct = "eighth" # deprecated because shadows a built-in function
octave = "eighth"
second = "2nd"
third = "3rd"
fourth = "4th"
fifth = "5th"
sixth = "6th"
seventh = "7th"
eighth = "eighth"
m2 = "m2"
M2 = "M2"
m3 = "m3"
M3 = "M3"
P4 = "P4"
TT = "TT"
P5 = "P5"
m6 = "m6"
M6 = "M6"
m7 = "m7"
M7 = "M7"
P8 = "P8"

# mapped to in-key steps
IN_KEY_INTERVALS = {
    second: 1,
    third: 2,
    fourth: 3,
    fifth: 4,
    sixth: 5,
    seventh: 6,
    oct: 7,
    eighth: 7,
}

# maps to semitones
FIXED_INTERVALS = {
    m2: 1,
    M2: 2,
    m3: 3,
    M3: 4,
    P4: 5,
    TT: 6,
    P5: 7,
    m6: 8,
    M6: 9,
    m7: 10,
    M7: 11,
    P8: 12,
}

global_key = None
def set_key(key):
    global global_key
    root, mode = key.split()
    assert root[0] in ("A", "B", "C", "D", "E", "F", "G")
    assert len(root) < 3
    if len(root) > 1: 
        assert root[1] in ("#", "b")
    assert mode.startswith("maj") or mode.startswith("min") or mode.startswith("phr")
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

    def __format__(self, format_spec):
        return format(str(self), format_spec)

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

    FIXME: if at some point we want to be able to add scale steps to a note not in the scale,
    below is a way of thinking about it that might be intuitive:

    Basically we've got a base note that's between two scale notes and we're being asked to 
    add/subtract to/from that note.  

    When I thought about it hard I assumed that it should round "away" from the 
    direction of the operation so round down when adding and round up when subtracting.
    E.g.: 

    1.5 + 1 = 2
    1.5 - 1 = 1
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
