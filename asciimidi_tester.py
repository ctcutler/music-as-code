from mido import Message

from asciimidi import ascii_to_midi
from midi import Config, midi_note_numbers, add_clock_messages

TICKS_PER_BEAT = 480
SYMBOLS_PER_BEAT = 2
TICKS_PER_NOTE = TICKS_PER_BEAT // SYMBOLS_PER_BEAT
VELOCITY = 60
CHANNEL = 0

def make_raw_note_message(mesg, raw_note, time):
    return Message(
        mesg,
        channel=CHANNEL,
        note=raw_note,
        velocity=VELOCITY,
        time=time
    )

def make_message(mesg, note, time, channel):
    return Message(
        mesg,
        channel=channel,
        note=midi_note_numbers[note[0]] + (int(note[1]) * 12),
        velocity=VELOCITY,
        time=time
    )

def on(note, time, channel=CHANNEL):
    return make_message('note_on', note, time, channel)

def off(note, time, channel=CHANNEL):
    return make_message('note_off', note, time, channel)

def test_ascii_to_midi(name, expected, notes, note_width, swing):
    config = Config(
        symbols_per_beat=SYMBOLS_PER_BEAT, 
        note_width=note_width, 
        swing=swing,
        beats_per_minute=90,
        midi_file_name='tester.mid'
    )
    (mid, ignore) = ascii_to_midi([notes], config)
    # assume only one track/voice
    actual = [mesg for mesg in mid.tracks[0] if not mesg.is_meta]
    if expected == actual:
        print(f"PASSED: {name}")
    else:
        e = [(mesg.note, mesg.time) for mesg in expected]
        a = [(mesg.note, mesg.time) for mesg in actual]
        print(f"FAILED: {name}\n{e}\n{a}")


notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 120), 
    on("B3", 120), off("B3", 120), 
    on("C3", 120), off("C3", 120), 
    on("D3", 120), off("D3", 120), 
]
test_ascii_to_midi("even steven", expected, notes, note_width=.5, swing=.5)

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("B3", 300), off("B3", 60), 
    on("C3", 60), off("C3", 60), 
    on("D3", 300), off("D3", 60), 
]
test_ascii_to_midi("swung", expected, notes, note_width=.5, swing=.75)

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 240), 
    on("B3", 0), off("B3", 240), 
    on("C3", 0), off("C3", 240), 
    on("D3", 0), off("D3", 240), 
]
test_ascii_to_midi("even legato", expected, notes, note_width=1, swing=.5)

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 120), 
    on("B3", 240), off("B3", 120), 
    on("C3", 0), off("C3", 120), 
    on("D3", 240), off("D3", 120), 
]
test_ascii_to_midi("swung legato", expected, notes, note_width=1, swing=.75)

notes = "A3 == C3 D3"
expected = [
    on("A3", 0), off("A3", 420), 
    on("C3", 60), off("C3", 60), 
    on("D3", 300), off("D3", 60), 
]
test_ascii_to_midi("tie within pair", expected, notes, note_width=.5, swing=.75)

notes = "A3 B3 == D3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("B3", 300), off("B3", 180), 
    on("D3", 300), off("D3", 60), 
]
test_ascii_to_midi("tie in two pairs", expected, notes, note_width=.5, swing=.75)

notes = "A3 B3 == == == F3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("B3", 300), off("B3", 660), 
    on("F3", 300), off("F3", 60), 
]
test_ascii_to_midi("tie over a pair", expected, notes, note_width=.5, swing=.75)

notes = "-- -- C3 D3"
expected = [
    on("C3", 480), off("C3", 60), 
    on("D3", 300), off("D3", 60), 
]
test_ascii_to_midi("rest within pair", expected, notes, note_width=.5, swing=.75)

notes = "A3 -- -- D3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("D3", 780), off("D3", 60), 
]
test_ascii_to_midi("rest in two pairs", expected, notes, note_width=.5, swing=.75)

notes = "A3 -- -- -- -- F3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("F3", 1260), off("F3", 60), 
]
test_ascii_to_midi("rest over a pair", expected, notes, note_width=.5, swing=.75)


# clock messages
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
if actual == expected:
    print("PASSED: clock messages")
else:
    e = [(mesg.type, mesg.time) for mesg in expected]
    a = [(mesg.type, mesg.time) for mesg in actual]
    print(f"FAILED: clock messages\n{e}\n{a}")


notes = "10 === --- 100"
expected = [
    make_raw_note_message('note_on', 10, 0),
    make_raw_note_message('note_off', 10, 360),
    make_raw_note_message('note_on', 100, 360),
    make_raw_note_message('note_off', 100, 120),
]
test_ascii_to_midi("raw notes", expected, notes, note_width=.5, swing=.5)



