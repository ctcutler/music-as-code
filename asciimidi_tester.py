from asciimidi import ascii_to_midi, get_midi_note, Config, add_clock_messages
from mido import Message

TICKS_PER_BEAT = 480
SYMBOLS_PER_BEAT = 2
TICKS_PER_NOTE = TICKS_PER_BEAT // SYMBOLS_PER_BEAT
VELOCITY = 60
CHANNEL = 0

def make_message(mesg, note, time):
    return Message(
        mesg,
        channel=CHANNEL,
        note=get_midi_note(note[0], note[1]),
        velocity=VELOCITY,
        time=time
    )

def on(note, time):
    return make_message('note_on', note, time)

def off(note, time):
    return make_message('note_off', note, time)

def test(name, expected, notes, note_width, swing):
    config = Config(
        symbols_per_beat=SYMBOLS_PER_BEAT, 
        note_width=note_width, 
        swing=swing,
        beats_per_minute=90,
        midi_file_name='tester.mid'
    )
    mid = ascii_to_midi([notes], config)
    # assume only one track/voice
    actual = [mesg for mesg in mid.tracks[0] if not mesg.is_meta]
    if expected == actual:
        print(f"{name} PASSED")
    else:
        e = [(mesg.note, mesg.time) for mesg in expected]
        a = [(mesg.note, mesg.time) for mesg in actual]
        print(f"{name} FAILED\n{e}\n{a}")

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 120), 
    on("B3", 120), off("B3", 120), 
    on("C3", 120), off("C3", 120), 
    on("D3", 120), off("D3", 120), 
]
test("even steven", expected, notes, note_width=.5, swing=.5)

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("B3", 300), off("B3", 60), 
    on("C3", 60), off("C3", 60), 
    on("D3", 300), off("D3", 60), 
]
test("swung", expected, notes, note_width=.5, swing=.75)

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 240), 
    on("B3", 0), off("B3", 240), 
    on("C3", 0), off("C3", 240), 
    on("D3", 0), off("D3", 240), 
]
test("even legato", expected, notes, note_width=1, swing=.5)

notes = "A3 B3 C3 D3"
expected = [
    on("A3", 0), off("A3", 120), 
    on("B3", 240), off("B3", 120), 
    on("C3", 0), off("C3", 120), 
    on("D3", 240), off("D3", 120), 
]
test("swung legato", expected, notes, note_width=1, swing=.75)

notes = "A3 == C3 D3"
expected = [
    on("A3", 0), off("A3", 420), 
    on("C3", 60), off("C3", 60), 
    on("D3", 300), off("D3", 60), 
]
test("tie within pair", expected, notes, note_width=.5, swing=.75)

notes = "A3 B3 == D3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("B3", 300), off("B3", 180), 
    on("D3", 300), off("D3", 60), 
]
test("tie in two pairs", expected, notes, note_width=.5, swing=.75)

notes = "A3 B3 == == == F3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("B3", 300), off("B3", 660), 
    on("F3", 300), off("F3", 60), 
]
test("tie over a pair", expected, notes, note_width=.5, swing=.75)

notes = "-- -- C3 D3"
expected = [
    on("C3", 480), off("C3", 60), 
    on("D3", 300), off("D3", 60), 
]
test("rest within pair", expected, notes, note_width=.5, swing=.75)

notes = "A3 -- -- D3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("D3", 780), off("D3", 60), 
]
test("rest in two pairs", expected, notes, note_width=.5, swing=.75)

notes = "A3 -- -- -- -- F3"
expected = [
    on("A3", 0), off("A3", 60), 
    on("F3", 1260), off("F3", 60), 
]
test("rest over a pair", expected, notes, note_width=.5, swing=.75)


# clock messages
note_messages = [
    Message('note_on', time=0),
    Message('note_off', time=1),
    Message('note_on', time=1),
    Message('note_off', time=1),
]
actual = add_clock_messages(note_messages, 60, 4)
expected = [
    Message('start', time=0),
    Message('clock', time=0),
    Message('note_on', time=0),
    Message('clock', time=.25),
    Message('clock', time=.5),
    Message('clock', time=.75),
    Message('clock', time=1),
    Message('note_off', time=1),
    Message('clock', time=1.25),
    Message('clock', time=1.5),
    Message('clock', time=1.75),
    Message('clock', time=2),
    Message('note_on', time=2),
    Message('clock', time=2.25),
    Message('clock', time=2.5),
    Message('clock', time=2.75),
    Message('clock', time=3),
    Message('note_off', time=3.0),
    Message('stop', time=3.0),
]
if actual == expected:
    print("clock messages PASSED")
else:
    e = [(mesg.type, mesg.time) for mesg in expected]
    a = [(mesg.type, mesg.time) for mesg in actual]
    print(f"clock messages FAILED\n{e}\n{a}")
