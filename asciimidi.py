from collections import namedtuple
import re
import sys
import time

from mido import MidiFile, MidiTrack, Message, MetaMessage, open_output, Backend, bpm2tempo

ASCII_NOTE_RE = re.compile('(\D*)(\d+)(\+*)(\-*)')
WS_RE = re.compile(' +')

CONFIG_FIELD_DEFAULTS = {
    "beats_per_minute": 120,
    "symbols_per_beat": 2, # 2 means each symbol is an 8th note
    "note_width": .5,          
    "swing": .5,               
    "midi_devices": ["FH-2"], # Or 'Elektron Model:Cycles' or 'IAC Driver Bus 1'     
    "midi_file_name": "new_song.mid",
    "loops": 1,
    # "beats_per_measure": 4, # haven't found a reason we need this yet
}
Config = namedtuple(
    'Config', 
    CONFIG_FIELD_DEFAULTS.keys(), 
    defaults=CONFIG_FIELD_DEFAULTS.values()
)

old_midi_note_numbers = {
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
midi_note_numbers = {
  'R': 0, 
  'C': 12, 
  'C#': 13,
  'Db': 13,
  'D': 14, 
  'D#': 15,
  'Eb': 15,
  'E': 16, 
  'F': 17,
  'F#': 18,
  'Gb': 18,
  'G': 19, 
  'G#': 20,
  'Ab': 20,
  'A': 21, 
  'A#': 22,
  'Bb': 22,
  'B': 23, 
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
            if symbol:
                midi_note = get_midi_note(symbol, octave)
            else:
                # when the symbol is missing, treat the octave as a MIDI note number (0-127) instead
                midi_note = int(octave)
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

def add_clock_messages(note_messages, qn_per_minute, pulses_per_qn):
    """
    Takes list of note messages where message.time is the offset in seconds since the previous
    note and returns a new list of note and clock messages where message.time is a 0-based offset
    (in seconds) from the start of the song.

    Adds in a MIDI start message at the beginning and a MIDI stop message at the end.
    """
    qn_per_second = qn_per_minute / 60
    pulses_per_second = qn_per_second * pulses_per_qn
    seconds_per_pulse = 1 / pulses_per_second
    all_messages = [Message('start', time=0.0)]
    next_clock = 0.0
    last_note = 0.0

    for message in note_messages:
        message.time += last_note
        last_note = message.time

        while next_clock <= message.time:
            all_messages.append(Message('clock', time=next_clock))
            next_clock += seconds_per_pulse
        all_messages.append(message)

    all_messages.append(Message('stop', time=all_messages[-1].time))
    return all_messages

def multi_port_play(midi_ports, config):
    midi_file = MidiFile(config.midi_file_name)
    messages = add_clock_messages(list(midi_file), config.beats_per_minute, 24)
    start_time = time.time()
    try:
        for message in messages:
            # after add_clock_messages, every message.time is a 0-based offset from
            # the start of the song, in seconds
            sleep_duration = (message.time + start_time) - time.time()
            if sleep_duration > 0.0:
                time.sleep(sleep_duration)
            if isinstance(message, MetaMessage):
                continue
            for midi_port in midi_ports:
                midi_port.send(message)
    except KeyboardInterrupt:
        for midi_port in midi_ports:
            midi_port.send(Message('stop', time=time.time()))
            midi_port.reset()
        sys.exit(1)

def play(asciis, config):
    ascii_to_midi(asciis, config)

    # user may pass None 
    if not config.midi_devices:
        return 

    backend = Backend()
    for i in range(config.loops):
        assert(len(config.midi_devices) < 3)

        if len(config.midi_devices) == 2:
            with (
                backend.open_output(config.midi_devices[0]) as midi_port1,
                backend.open_output(config.midi_devices[1]) as midi_port2
            ):
                multi_port_play([midi_port1, midi_port2], config)
        else: 
            with backend.open_output(config.midi_devices[0]) as midi_port:
                multi_port_play([midi_port], config)

