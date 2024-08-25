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

DEGREES = [ "I", "II", "III", "IV", "V", "VI", "VII" ]
MAJOR_SEMIS = [ 0, 2, 4, 5, 7, 9, 11 ]
MINOR_SEMIS = [ 0, 2, 3, 5, 7, 8, 10 ]
MAJOR_DEGREES_TO_SEMIS = dict(zip(DEGREES, MAJOR_SEMIS))
MAJOR_SEMIS_TO_DEGREES = dict(zip(MAJOR_SEMIS, DEGREES))
MINOR_DEGREES_TO_SEMIS = dict(zip(DEGREES, MINOR_SEMIS))
MINOR_SEMIS_TO_DEGREES = dict(zip(MINOR_SEMIS, DEGREES))
MINOR_DEGREES_TO_SEMIS = {
    "I": 0,
    "II": 2,
    "III": 3,
    "IV": 5,
    "V": 7,
    "VI": 8,
    "VII": 10,
}
MINOR_SEMIS_TO_DEGREES = dict((v,k) for k,v in MINOR_DEGREES_TO_SEMIS.items())
PITCHES = SHARP_PITCHES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
FLAT_PITCHES = ["A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]
INTERVAL_SEMITONES = {
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
INVERTED_INTERVAL_SEMITONES = {
    "m2": -11,
    "M2": -10,
    "m3": -9,
    "M3": -8,
    "P4": -7,
    "TT": -6,
    "P5": -5,
    "m6": -4,
    "M6": -3,
    "m7": -2,
    "M7": -1,
}

def add_semitones(note, semitones, adjust_octave=True):
    pitch, octave = note[:-1], int(note[-1])
    pitches = FLAT_PITCHES if pitch[-1] == "b" else SHARP_PITCHES
    i = pitches.index(pitch)
    i += semitones
    octave += i // len(pitches) if adjust_octave else 0
    pitch = pitches[i % len(pitches)]

    return pitch+str(octave)
    
def scale_note(key, mode, degree, octave):
    if mode == "major":
        degrees_to_semis = MAJOR_DEGREES_TO_SEMIS
    elif mode == "minor":
        degrees_to_semis = MINOR_DEGREES_TO_SEMIS
    else:
        raise Exception(f"Unknown mode: {mode}")

    return add_semitones(key+str(octave), degrees_to_semis[degree], adjust_octave=False)

def interval(base_note, interval_type, inverted=False):
    """
    Takes a base note and an interval type and returns a (potentially inverted)
    interval note.  See INTERVAL_STEPS for allowed interval types.
    """
    interval_semitones = INVERTED_INTERVAL_SEMITONES if inverted else INTERVAL_SEMITONES
    return add_semitones(base_note, interval_semitones[interval_type])

def semitone_distance(pitch1, pitch2):
    """
    returns the number of semitones between pitch1 and pitch2; if pitch2 is lower than pitch1
    pitch2 is assumed to be an octave above
    """
    pitch1_semis = FLAT_PITCHES.index(pitch1) if pitch1[-1] == "b" else PITCHES.index(pitch1) 
    pitch2_semis = FLAT_PITCHES.index(pitch2) if pitch2[-1] == "b" else PITCHES.index(pitch2) 
    if pitch2_semis >= pitch1_semis:
        return pitch2_semis - pitch1_semis
    else:
        return (len(PITCHES) + pitch2_semis) - pitch1_semis

def degree(key, mode, pitch):
    semis = semitone_distance(key, pitch)
    if mode == "major":
        semis_to_degrees = MAJOR_SEMIS_TO_DEGREES
    elif mode == "minor":
        semis_to_degrees = MINOR_SEMIS_TO_DEGREES
    else:
        raise Exception(f"Unknown mode: {mode}")

    return semis_to_degrees[semis]

def scale_interval(key, mode, base_note, interval_size):
    """
    Takes a key, a base note, and an interval size (2-8) and return a
    note that makes an interval of that size within the scale. 
    """

    # find the degree
    pitch, octave = base_note[:-1], int(base_note[-1])
    base_degree = degree(key, mode, pitch)
    base_degree_index = DEGREES.index(base_degree)
    c_degree = degree(key, mode, "C")
    c_degree_index = DEGREES.index(c_degree)
    interval_degree_index = base_degree_index + (interval_size-1)

    # Use degree indexes (avoids comparing roman numeral degrees) to determine
    # whether the interval degree is above or below the C (that is, in turn, above
    # base degree).  This is totally obvious, right?
    if c_degree_index < base_degree_index:
        c_degree_index += len(DEGREES)
    if interval_degree_index >= c_degree_index and c_degree_index != base_degree_index:
        octave += 1

    if interval_degree_index >= len(DEGREES):
        interval_degree_index -= len(DEGREES)

    return scale_note(key, mode, DEGREES[interval_degree_index], octave)
