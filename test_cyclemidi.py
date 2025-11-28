import pytest

from mido import Message, MidiFile, MidiTrack, MetaMessage

from midi import midi_note_numbers
from cyclemidi import notes, rhythm

VELOCITY = 5
CHANNEL = 0


def make_message(mesg, note, time, channel, velocity):
    return Message(
        mesg,
        channel=channel,
        note=midi_note_numbers[note[0]] + (int(note[1]) * 12),
        velocity=int((velocity / 9) * 127),
        time=time,
    )


def on(note, time, channel=CHANNEL, velocity=VELOCITY):
    return make_message("note_on", note, time, channel, velocity)


def off(note, time, channel=CHANNEL, velocity=VELOCITY):
    return make_message("note_off", note, time, channel, velocity)


@pytest.fixture
def mid_factory():
    def factory(voices):
        set_tempo_message = MetaMessage("set_tempo", tempo=500000, time=0)
        tracks = [MidiTrack([set_tempo_message] + messages) for messages in voices]
        return MidiFile(tracks=tracks)

    return factory


# 480 ticks per 4/4 quarter note
# 1920 ticks per bar/cycle
# 640 ticks per 3/4 quarter note
# 320 ticks between ons and offs at 50% note length


def test_one_level_one_cycle(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 320),
                on("B3", 320),
                off("B3", 320),
                on("C3", 320),
                off("C3", 320),
            ]
        ]
    )
    actual = notes("[A3 B3 C3]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_one_level_three_cycles(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 960),
                on("B3", 960),
                off("B3", 960),
                on("C3", 960),
                off("C3", 960),
            ]
        ]
    )
    actual = notes("<[A3] [B3] [C3]>").midi().midi_file
    assert expected.tracks == actual.tracks


def test_three_level_nesting(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 320),
                on("B3", 320),
                off("B3", 320),
                on("C3", 320),
                off("C3", 320),
                on("A3", 320),
                off("A3", 320),
                on("B3", 320),
                off("B3", 320),
                on("C3", 320),
                off("C3", 160),
                on("D3", 160),
                off("D3", 160),
            ]
        ]
    )
    actual = notes("[A3 B3 C3] [A3 B3 [C3 D3]]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_crazy_whitespace(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 320),
                on("B3", 320),
                off("B3", 320),
                on("C3", 320),
                off("C3", 320),
            ]
        ]
    )
    actual = (
        notes(""" [ A3       B3 C3
          ] """)
        .midi()
        .midi_file
    )
    assert expected.tracks == actual.tracks


def test_polyphony(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, 0),
                off("A3", 320, 0),
                on("B3", 320, 0),
                off("B3", 320, 0),
                on("C3", 320, 0),
                off("C3", 320, 0),
            ],
            [
                on("C3", 640, 1),
                off("C3", 320, 1),
                on("E3", 320, 1),
                off("E3", 320, 1),
            ],
            [
                on("D3", 640, 2),
                off("D3", 320, 2),
            ],
        ]
    )
    actual = notes("[A3 B3,C3,D3 C3,E3]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_25_percent_note_width(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 160),
                on("B3", 480),
                off("B3", 160),
                on("C3", 480),
                off("C3", 160),
            ],
        ]
    )
    actual = notes("[A3 B3 C3]").set_config("note_width", 0.25).midi().midi_file
    assert expected.tracks == actual.tracks


def test_rests(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 384),
                off("A3", 192),
                on("B3", 192),
                off("B3", 192),
                on("C3", 192 + 384),
                off("C3", 192),
            ],
        ]
    )
    actual = notes("[~ A3 B3 ~ C3]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_polyphonic_rests(mid_factory):
    expected = mid_factory(
        [
            [
                on("E4", 0, 0),
                off("E4", 240, 0),
                on("E4", 240 + 480, 0),
                off("E4", 240, 0),
                on("E4", 240, 0),
                off("E4", 240, 0),
            ],
            [
                on("G4", 0, 1),
                off("G4", 240, 1),
                on("G4", 240 + 480, 1),
                off("G4", 240, 1),
                on("G4", 240, 1),
                off("G4", 240, 1),
            ],
        ]
    )
    actual = notes("[ E4,G4 ~ E4,G4 E4,G4 ]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_stacked_cycles(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, 0),
                off("A3", 320, 0),
                on("B3", 320, 0),
                off("B3", 320, 0),
                on("C3", 320, 0),
                off("C3", 320, 0),
                on("A3", 320, 0),
                off("A3", 320, 0),
                on("B3", 320, 0),
                off("B3", 320, 0),
                on("C3", 320, 0),
                off("C3", 320, 0),
            ],
            [
                on("A3", 0, 1),
                off("A3", 240, 1),
                on("B3", 240, 1),
                off("B3", 240, 1),
                on("C3", 240, 1),
                off("C3", 240, 1),
                on("D3", 240, 1),
                off("D3", 240, 1),
                on("A4", 240, 1),
                off("A4", 240, 1),
                on("B4", 240, 1),
                off("B4", 240, 1),
                on("C4", 240, 1),
                off("C4", 240, 1),
                on("D4", 240, 1),
                off("D4", 240, 1),
            ],
        ]
    )
    actual = (
        notes("[A3 B3 C3]")
        .stack()
        .notes("[A3 B3 C3 D3] [A4 B4 C4 D4]")
        .midi()
        .midi_file
    )
    assert expected.tracks == actual.tracks


def test_merged_cycles(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, velocity=9),
                off("A3", 320, velocity=9),
                on("B3", 320, velocity=9),
                off("B3", 320, velocity=9),
                on("C3", 320, velocity=5),
                off("C3", 320, velocity=5),
            ],
        ]
    )
    actual = notes("[A3 B3 C3]").velocity("[9 9 5]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_merged_cycles_same_length_different_rhythm(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, velocity=7),
                off("A3", 320, velocity=7),
                on("B3", 320, velocity=7),
                off("B3", 320, velocity=7),
                on("C3", 320, velocity=8),
                off("C3", 320, velocity=8),
            ],
        ]
    )
    actual = notes("[A3 B3 C3]").velocity("[7 8]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_merged_cycles_different_length_same_rhythm(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, velocity=7),
                off("A3", 960, velocity=7),
                on("B3", 960, velocity=8),
                off("B3", 960, velocity=8),
                on("C3", 960, velocity=7),
                off("C3", 960, velocity=7),
                on("A3", 960, velocity=8),
                off("A3", 960, velocity=8),
                on("B3", 960, velocity=7),
                off("B3", 960, velocity=7),
                on("C3", 960, velocity=8),
                off("C3", 960, velocity=8),
            ],
        ]
    )
    actual = notes("[A3] [B3] [C3]").velocity("[7] [8]").midi().midi_file
    assert expected.tracks == actual.tracks


@pytest.mark.skip(reason="Don't think we should support polyphony mismatches")
def test_more_voices_in_merger(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, velocity=7),
                off("A3", 480, velocity=7),
                on("C3", 480, velocity=9),
                off("C3", 480, velocity=9),
            ],
            [
                on("B3", 0, 1, velocity=8),
                off("B3", 480, 1, velocity=8),
            ],
        ]
    )
    actual = notes("[A3,B3 C3]").velocity("[7,8,9 9]").midi().midi_file
    assert expected.tracks == actual.tracks


@pytest.mark.skip(reason="Don't think we should support polyphony mismatches")
def test_more_voices_in_mergee(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0, velocity=7),
                off("A3", 480, velocity=7),
                on("C3", 480, velocity=9),
                off("C3", 480, velocity=9),
            ],
            [
                on("B3", 0, 1, velocity=7),
                off("B3", 480, 1, velocity=7),
            ],
        ]
    )
    actual = notes("[A3,B3 C3]").velocity("[7 9]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_rhythm_monophonic(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 480),
                on("A3", 480),
                off("A3", 240),
                on("A3", 240),
                off("A3", 240),
                on("B3", 240),
                off("B3", 480),
                on("B3", 480),
                off("B3", 240),
                on("B3", 240),
                off("B3", 240),
            ],
        ]
    )
    actual = rhythm("[x [x x]]").notes("[A3] [B3]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_rhythm_polyphonic(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 480),
                on("A3", 480),
                off("A3", 240),
                on("A3", 240),
                off("A3", 240),
                on("B3", 240),
                off("B3", 480),
                on("B3", 480),
                off("B3", 240),
                on("B3", 240),
                off("B3", 240),
            ],
            [
                on("C3", 0, 1),
                off("C3", 480, 1),
                on("C3", 480, 1),
                off("C3", 240, 1),
                on("C3", 240, 1),
                off("C3", 240, 1),
                on("D3", 240, 1),
                off("D3", 480, 1),
                on("D3", 480, 1),
                off("D3", 240, 1),
                on("D3", 240, 1),
                off("D3", 240, 1),
            ],
        ]
    )
    actual = rhythm("[x,x [x,x x,x]]").notes("[A3,C3] [B3,D3]").midi().midi_file
    assert expected.tracks == actual.tracks


@pytest.mark.skip(reason="Don't think we should support polyphony mismatches")
def test_rhythm_mismatched_polyphonic(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 480),
                on("A3", 480),
                off("A3", 240),
                on("A3", 240),
                off("A3", 240),
                on("B3", 240),
                off("B3", 480),
                on("B3", 480),
                off("B3", 240),
                on("B3", 240),
                off("B3", 240),
            ],
            [
                on("C3", 0, 1),
                off("C3", 480, 1),
                on("C3", 480, 1),
                off("C3", 240, 1),
                on("C3", 240, 1),
                off("C3", 240, 1),
                on("D3", 240, 1),
                off("D3", 480, 1),
                on("D3", 480, 1),
                off("D3", 240, 1),
                on("D3", 240, 1),
                off("D3", 240, 1),
            ],
        ]
    )
    actual = rhythm("[x [x x]]").notes("[A3,C3] [B3,D3]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_rhythm_mismatched_rests(mid_factory):
    expected = mid_factory(
        [
            [
                on("A3", 0),
                off("A3", 480),
                on("A3", 960),
                off("A3", 240),
                on("B3", 240),
                off("B3", 480),
                on("B3", 960),
                off("B3", 240),
            ],
        ]
    )
    actual = rhythm("[x [~ x]]").notes("[A3] [B3]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_tie_within_cycle(mid_factory):
    expected = mid_factory(
        [
            [
                on("A4", 0),
                off("A4", 240),
                on("C5", 240),
                off("C5", 480),
                on("D5", 480),
                off("D5", 240),
            ],
        ]
    )
    actual = notes("[ A4 C5 - D5 ]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_tie_across_cycles(mid_factory):
    expected = mid_factory(
        [
            [
                on("A4", 0),
                off("A4", 480),
                on("E5", 480),
                off("E5", 960 + 480),
                on("D5", 480),
                off("D5", 480),
            ],
        ]
    )
    actual = notes("[ A4 E5 ] [ - D5 ]").midi().midi_file
    assert expected.tracks == actual.tracks


def test_two_ties_across_cycles(mid_factory):
    expected = mid_factory(
        [
            [
                on("A4", 0),
                off("A4", 480),
                on("E5", 480),
                off("E5", 960 + 480),
                on("D5", 480),
                off("D5", 240),
                on("G4", 240),
                off("G4", 240),
            ],
        ]
    )
    actual = notes("[ A4 E5 ] [ - - D5 G4 ]").midi().midi_file
    assert expected.tracks == actual.tracks
