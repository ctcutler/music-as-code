from dataclasses import dataclass
import pytest

from mido import Message

from asciimidi import ascii_to_midi
from midi import Config, midi_note_numbers, add_clock_messages

SYMBOLS_PER_BEAT = 2
VELOCITY = 70
CHANNEL = 0
SWING = .5
NOTE_WIDTH = .5

@pytest.fixture
def config():
    return Config(
        symbols_per_beat=SYMBOLS_PER_BEAT, 
        note_width=NOTE_WIDTH, 
        swing=SWING,
        beats_per_minute=90,
        midi_file_name='tester.mid'
    )

@dataclass
class Note:
    note:str
    start:int = None
    stop:int = None
    channel:int = CHANNEL

@pytest.fixture
def note_factory():
    def factory(notes):
        messages = []
        for note in notes:
            messages.extend([
                Message(
                    'note_on',
                    channel=note.channel,
                    note=midi_note_numbers[note.note[0]] + (int(note.note[1]) * 12),
                    velocity=VELOCITY,
                    time=note.start
                ),
                Message(
                    'note_off',
                    channel=note.channel,
                    note=midi_note_numbers[note.note[0]] + (int(note.note[1]) * 12),
                    velocity=VELOCITY,
                    time=note.stop
                ),
            ])
        return messages

    return factory

def test_even_steven(config, note_factory):
    notes = "A3 B3 C3 D3"
    expected = note_factory([
        Note("A3", 0, 120),
        Note("B3", 120, 120),
        Note("C3", 120, 120),
        Note("D3", 120, 120),
    ])

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_swung(config, note_factory):
    notes = "A3 B3 C3 D3"
    expected = note_factory([
        Note("A3", 0, 60),
        Note("B3", 300, 60),
        Note("C3", 60, 60),
        Note("D3", 300, 60),
    ])
    config.note_width = 0.5
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_even_legato(config, note_factory):
    notes = "A3 B3 C3 D3"
    expected = note_factory([
        Note("A3", 0, 240),
        Note("B3", 0, 240),
        Note("C3", 0, 240),
        Note("D3", 0, 240),
    ])
    config.note_width = 1 

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_swung_legato(config, note_factory):
    notes = "A3 B3 C3 D3"
    expected = note_factory([
        Note("A3", 0, 120),
        Note("B3", 240, 120),
        Note("C3", 0, 120),
        Note("D3", 240, 120),
    ])
    config.note_width = 1 
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_tie_wthin_pair(config, note_factory):
    notes = "A3 == C3 D3"
    expected = note_factory([
        Note("A3", 0, 420),
        Note("C3", 60, 60),
        Note("D3", 300, 60),
    ])
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_tie_two_pairs(config, note_factory):
    notes = "A3 B3 == D3"
    expected = note_factory([
        Note("A3", 0, 60),
        Note("B3", 300, 180),
        Note("D3", 300, 60),
    ])
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_tie_over_a_pair(config, note_factory):
    notes = "A3 B3 == == == F3"
    expected = note_factory([
        Note("A3", 0, 60),
        Note("B3", 300, 660),
        Note("F3", 300, 60),
    ])
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_rest_within_pair(config, note_factory):
    notes = "-- -- C3 D3"
    expected = note_factory([
        Note("C3", 480, 60),
        Note("D3", 300, 60),
    ])
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_rest_in_two_pairs(config, note_factory):
    notes = "A3 -- -- D3"
    expected = note_factory([
        Note("A3", 0, 60),
        Note("D3", 780, 60),
    ])
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_rest_over_a_pair(config, note_factory):
    notes = "A3 -- -- -- -- F3"
    expected = note_factory([
        Note("A3", 0, 60),
        Note("F3", 1260, 60),
    ])
    config.swing = 0.75

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

def test_clock_messages():
    note_messages = [
        Message('note_on', time=0),
        Message('note_off', time=1),
        Message('note_on', time=1),
        Message('note_off', time=1),
    ]
    actual = add_clock_messages(note_messages, 60, 4)
    expected = [
        Message('start', time=0.0),
        Message('clock', time=0.0),
        Message('note_on', time=0.0),
        Message('clock', time=.25),
        Message('clock', time=.5),
        Message('clock', time=.75),
        Message('clock', time=1.0),
        Message('note_off', time=1.0),
        Message('clock', time=1.25),
        Message('clock', time=1.5),
        Message('clock', time=1.75),
        Message('clock', time=2.0),
        Message('note_on', time=2.0),
        Message('clock', time=2.25),
        Message('clock', time=2.5),
        Message('clock', time=2.75),
        Message('clock', time=3.0),
        Message('note_off', time=3.0),
    ]
    assert actual == expected

def test_raw_notes(config, note_factory):
    def make_raw_note_message(mesg, raw_note, time):
        return Message(
            mesg,
            channel=CHANNEL,
            note=raw_note,
            velocity=VELOCITY,
            time=time
        )

    notes = "10 === --- 100"
    expected = [
        make_raw_note_message('note_on', 10, 0),
        make_raw_note_message('note_off', 10, 360),
        make_raw_note_message('note_on', 100, 360),
        make_raw_note_message('note_off', 100, 120),
    ]

    (mid, ignore) = ascii_to_midi([notes], config)
    assert expected == [mesg for mesg in mid.tracks[0] if not mesg.is_meta]

