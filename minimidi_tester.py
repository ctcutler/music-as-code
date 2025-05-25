from fractions import Fraction

from mido import Message

from midi import Config, midi_note_numbers
from minimidi import Cycle, Event, parse_mini, expand_alternatives, generate_events, mini_to_midi

VELOCITY = 60
CHANNEL = 0

def test(name, expected, actual):
    if expected == actual:
        print(f"PASSED: {name}")
    else:
        print(f"FAILED: {name}\nexpected: {expected}\nactual: {actual}")

def test_raises(name, func, param):
    try:
        func(param)
    except:
        print(f"PASSED: {name}")
    else:
        print(f"FAILED: {name} No exception thrown!")

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

def test_mini_to_midi(name, expected, mini, note_width=.5):
    config = Config(
        beats_per_minute=90,
        note_width=note_width,
        midi_file_name='tester.mid'
    )
    (mid, ignore) = mini_to_midi(mini, config)

    actual = []
    for track in mid.tracks:
        track_messages = []
        for mesg in track:
            if not mesg.is_meta:
                track_messages.append(mesg)

        actual.append(track_messages)

    if expected == actual:
        print(f"PASSED: {name}")
    else:
        e = []
        for track in expected:
            track_messages = []
            for mesg in track:
                if not mesg.is_meta:
                    track_messages.append((mesg.note, mesg.time, mesg.channel))
            e.append(track_messages)
        a = []
        for track in actual:
            track_messages = []
            for mesg in track:
                if not mesg.is_meta:
                    track_messages.append((mesg.note, mesg.time, mesg.channel))
            a.append(track_messages)

        print(f"FAILED: {name}\n{e}\n{a}")

test(
    "one level, one cycle",
    [
        Cycle([ 
               [Event("a")], 
               [Event("b")], 
               [Event("c")], 
        ])
    ],
    parse_mini("[a b c]")
)

test(
    "one level, three cycles",
    [
        Cycle([[Event("a")]]),
        Cycle([[Event("b")]]),
        Cycle([[Event("c")]]),
    ],
    parse_mini("<[a] [b] [c]>")
)

test(
    "three level nesting",
    [
        Cycle([
            [Event("a")], 
            [Event("b")], 
            [Event("c")], 
        ]),
        Cycle([
            [Event("a")], 
            [Event("b")], 
            Cycle([
                [Event("c")], 
                [Event("d")], 
            ])
        ])
    ],
    parse_mini("[ a b c ] [a b [c d]]")
)

test(
    "crazy whitespace",
    [
        Cycle([
            [Event("a")], 
            [Event("b")], 
            [Event("c")], 
        ])
    ],
    parse_mini(""" [ a       b c
          ] """)
)

test(
    "polyphony",
    [
        Cycle([
            [Event("a")],
            [Event("b"), Event("c"), Event("d")],
            [Event("c"), Event("e")],
        ])
    ],
    parse_mini("[a b,c,d c,e]")
)

test_raises("test open without close", parse_mini, "[a b c")
test_raises("close without open", parse_mini, "a b c]")
test_raises("top level without brackets", parse_mini, "a b c")

test(
    "expand simple AC",
    "[a b c] [a b d]",
    expand_alternatives("[a b <c d>]")
)

test(
    "expand non-nested ACs",
    "[a b c [e f]] [a b c [e g]] [a b d [e f]] [a b d [e g]]",
    expand_alternatives("[a b <c d> [e <f g>]]")
)

test(
    "expand nested ACs",
    "[a b c] [a b d] [a b c] [a b e]",
    expand_alternatives("[a b <c <d e>>]")
)

test(
    "simple generation",
    [
        [
            Event('a', Fraction(0, 1), Fraction(1, 3)),
            Event('b', Fraction(1, 3), Fraction(2, 3)),
            Event('c', Fraction(2, 3), Fraction(1, 1))
        ]
    ],
    generate_events(parse_mini("[a b c]"))
)

test(
    "nested generation",
    [
        [
            Event('a', Fraction(0, 1), Fraction(1, 4)),
            Event('b', Fraction(1, 4), Fraction(1, 2)),
            Event('c', Fraction(1, 2), Fraction(1, 1))
        ]
    ],
    generate_events(parse_mini("[[a b] c]"))
)


test(
    "simple alternatives",
    [
        [
            Event('a', Fraction(0, 1), Fraction(1, 1)),
            Event('b', Fraction(1, 1), Fraction(2, 1)),
            Event('c', Fraction(2, 1), Fraction(3, 1))
        ]
    ],
    generate_events(parse_mini("<[a] [b] [c]>"))
)

test(
    "polyphony generation",
    [
        [
            Event("a", Fraction(0, 1), Fraction(1, 3)),
            Event("b", Fraction(1, 3), Fraction(2, 3)),
            Event("d", Fraction(2,3), Fraction(1, 1)),
        ],
        [
            Event("c", Fraction(1, 3), Fraction(2, 3)),
            Event("e", Fraction(2,3), Fraction(1, 1)),
        ],
        [
            Event("d", Fraction(1, 3), Fraction(2, 3)),
        ],
    ],
    generate_events(parse_mini("[a b,c,d d,e]"))
)

test_raises("test open without close", parse_mini, "[a b c")
test_raises("close without open", parse_mini, "a b c]")
test_raises("top level without brackets", parse_mini, "a b c")

# 480 ticks per 4/4 quarter note
# 1920 ticks per bar/cycle
# 640 ticks per 3/4 quarter note
# 320 ticks between ons and offs at 50% note length
expected = [[
    on("A3", 0), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 320), 
]]
test_mini_to_midi("mini: one level one cycle", expected, "[A3 B3 C3]")
expected = [[
    on("A3", 0), off("A3", 960), 
    on("B3", 960), off("B3", 960), 
    on("C3", 960), off("C3", 960), 
]]
test_mini_to_midi("mini: one level three cycles", expected, "<[A3] [B3] [C3]>")
expected = [[
    on("A3", 0), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 320), 
    on("A3", 320), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 160), 
    on("D3", 160), off("D3", 160), 
]]
test_mini_to_midi("mini: three level nesting", expected, "[A3 B3 C3] [A3 B3 [C3 D3]]")
expected = [[
    on("A3", 0), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 320), 
]]
test_mini_to_midi("mini: crazy whitespace", expected, """ [ A3       B3 C3
          ] """)
expected = [
    [
        on("A3", 0, 0), off("A3", 320, 0), 
        on("B3", 320, 0), off("B3", 320, 0), 
        on("C3", 320, 0), off("C3", 320, 0), 
    ],
    [
        on("C3", 640, 1), off("C3", 320, 1), 
        on("E3", 320, 1), off("E3", 320, 1), 
    ],
    [
        on("D3", 640, 2), off("D3", 320, 2), 
    ],
]
test_mini_to_midi("mini: polyphony", expected, "[A3 B3,C3,D3 C3,E3]")

expected = [[
    on("A3", 0), off("A3", 160), 
    on("B3", 480), off("B3", 160), 
    on("C3", 480), off("C3", 160), 
]]
test_mini_to_midi("mini: 25% note width", expected, "[A3 B3 C3]", note_width=.25)

expected = [[
    on("A3", 384), off("A3", 192), 
    on("B3", 192), off("B3", 192), 
    on("C3", 192+384), off("C3", 192), 
]]
test_mini_to_midi("mini: rests", expected, "[~ A3 B3 ~ C3]")

expected = [
    [
        on("E4", 0, 0), off("E4", 240, 0), 
        on("E4", 240+480, 0), off("E4", 240, 0), 
        on("E4", 240, 0), off("E4", 240, 0), 
    ],
    [
        on("G4", 0, 1), off("G4", 240, 1), 
        on("G4", 240+480, 1), off("G4", 240, 1), 
        on("G4", 240, 1), off("G4", 240, 1), 
    ],
]
test_mini_to_midi("mini: polyphonic rests", expected, "[ E4,G4 ~ E4,G4 E4,G4 ]")

expected = [
    [
        on("A3", 0, 0), off("A3", 320, 0), 
        on("B3", 320, 0), off("B3", 320, 0), 
        on("C3", 320, 0), off("C3", 320, 0), 
    ],
    [
        on("A3", 0, 1), off("A3", 240, 1), 
        on("B3", 240, 1), off("B3", 240, 1), 
        on("C3", 240, 1), off("C3", 240, 1), 
        on("D3", 240, 1), off("D3", 240, 1), 
        on("A4", 240, 1), off("A4", 240, 1), 
        on("B4", 240, 1), off("B4", 240, 1), 
        on("C4", 240, 1), off("C4", 240, 1), 
        on("D4", 240, 1), off("D4", 240, 1), 
    ]
]
test_mini_to_midi("mini: stacked cycles", expected, ["[A3 B3 C3]", "[A3 B3 C3 D3] [A4 B4 C4 D4]"])
