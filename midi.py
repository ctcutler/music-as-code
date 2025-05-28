from collections import namedtuple
from dataclasses import dataclass, field
import re
import sys
import time

from mido import MidiFile, Message, MetaMessage, open_output, Backend


@dataclass
class Config:
    beats_per_minute: int = 120
    symbols_per_beat: int = 2 # 2 means each symbol is an 8th note
    note_width: float = .5          
    swing: float = .5               
    midi_devices: list = field(default_factory=lambda: ["FH-2"]) # Or 'Elektron Model:Cycles' or 'IAC Driver Bus 1'     
    midi_file_name: str = "new_song.mid"
    beats_per_measure: int = 4

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

ASCII_NOTE_RE = re.compile('(\D*)(\d+)(\+*)(\-*)')

def get_midi_note_and_velocity(symbol):
    m = ASCII_NOTE_RE.search(symbol)
    note_name, octave, up_volume, down_volume = m.groups()
    if note_name:
        midi_note = midi_note_numbers[note_name] + (int(octave) * 12)
    else:
        # when the symbol is missing, treat the octave as a MIDI note number (0-127) instead
        midi_note = int(octave)
    velocity = 60 
    velocity += 20 * len(up_volume) 
    velocity -= 20 * len(down_volume) 

    return midi_note, velocity

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

    #all_messages.append(Message('stop', time=all_messages[-1].time))
    return all_messages

def multi_port_play(midi_ports, config, total_secs):
    midi_file = MidiFile(config.midi_file_name)
    messages = add_clock_messages(list(midi_file), config.beats_per_minute, 24)
    start_time = time.time()
    first_loop = True
    try:
        while True:
            for message in messages:
                # after add_clock_messages, every message.time is a 0-based offset from
                # the start of the song, in seconds... we need to adjust on every successive
                # loop
                if not first_loop:
                    message.time += total_secs

                sleep_duration = (message.time + start_time) - time.time()

                if sleep_duration > 0.0:
                    time.sleep(sleep_duration)

                if not isinstance(message, MetaMessage):
                    for midi_port in midi_ports:
                        midi_port.send(message)
            first_loop = False
    except KeyboardInterrupt:
        for midi_port in midi_ports:
            midi_port.send(Message('stop', time=time.time()))
            midi_port.reset()
        sys.exit(1)

def play_midi(config, total_secs):
    # user may pass None 
    if not config.midi_devices:
        return 

    backend = Backend()
    assert(len(config.midi_devices) < 3)

    if len(config.midi_devices) == 2:
        with (
            backend.open_output(config.midi_devices[0]) as midi_port1,
            backend.open_output(config.midi_devices[1]) as midi_port2
        ):
            multi_port_play([midi_port1, midi_port2], config, total_secs)
    else: 
        with backend.open_output(config.midi_devices[0]) as midi_port:
            multi_port_play([midi_port], config, total_secs)

