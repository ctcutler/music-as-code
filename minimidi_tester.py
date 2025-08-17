from fractions import Fraction

from mido import Message

from midi import Config, midi_note_numbers
from minimidi import Cycle, Event, parse_mini, expand_alternatives, generate_events, notes, rhythm

VELOCITY = 5
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

def make_message(mesg, note, time, channel, velocity):
    return Message(
        mesg,
        channel=channel,
        note=midi_note_numbers[note[0]] + (int(note[1]) * 12),
        velocity=int((velocity/9)*127),
        time=time,
    )

def on(note, time, channel=CHANNEL, velocity=VELOCITY):
    return make_message('note_on', note, time, channel, velocity)

def off(note, time, channel=CHANNEL, velocity=VELOCITY):
    return make_message('note_off', note, time, channel, velocity)

def compare_midi(name, mid, expected):
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
                    track_messages.append((mesg.note, mesg.time, mesg.channel, mesg.velocity))
            e.append(track_messages)
        a = []
        for track in actual:
            track_messages = []
            for mesg in track:
                if not mesg.is_meta:
                    track_messages.append((mesg.note, mesg.time, mesg.channel, mesg.velocity))
            a.append(track_messages)

        print(f"FAILED: {name}\n{e}\n{a}")

def test_mini(name, expected, mini_obj):
    compare_midi(name, mini_obj.midi().midi_file, expected)

test(
    "parse_mini one level, one cycle",
    [
        Cycle([ 
               ["a"], 
               ["b"], 
               ["c"], 
        ])
    ],
    parse_mini("[a b c]")
)

test(
    "parse_mini one level, three cycles",
    [
        Cycle([["a"]]),
        Cycle([["b"]]),
        Cycle([["c"]]),
    ],
    parse_mini("<[a] [b] [c]>")
)

test(
    "parse_mini three level nesting",
    [
        Cycle([
            ["a"], 
            ["b"], 
            ["c"], 
        ]),
        Cycle([
            ["a"], 
            ["b"], 
            Cycle([
                ["c"], 
                ["d"], 
            ])
        ])
    ],
    parse_mini("[ a b c ] [a b [c d]]")
)

test(
    "parse_mini crazy whitespace",
    [
        Cycle([
            ["a"], 
            ["b"], 
            ["c"], 
        ])
    ],
    parse_mini(""" [ a       b c
          ] """)
)

test(
    "parse_mini polyphony",
    [
        Cycle([
            ["a"],
            ["b", "c", "d"],
            ["c", "e"],
        ])
    ],
    parse_mini("[a b,c,d c,e]")
)

test_raises("parse_mini test open without close", parse_mini, "[a b c")
test_raises("parse_mini close without open", parse_mini, "a b c]")
test_raises("parse_mini top level without brackets", parse_mini, "a b c")

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
            Event(Fraction(0, 1), Fraction(1, 3), 'a'),
            Event(Fraction(1, 3), Fraction(2, 3), 'b'),
            Event(Fraction(2, 3), Fraction(1, 1), 'c')
        ]
    ],
    generate_events(parse_mini("[a b c]"), "NOTES")
)

test(
    "nested generation",
    [
        [
            Event(Fraction(0, 1), Fraction(1, 4), 'a'),
            Event(Fraction(1, 4), Fraction(1, 2), 'b'),
            Event(Fraction(1, 2), Fraction(1, 1), 'c')
        ]
    ],
    generate_events(parse_mini("[[a b] c]"), "NOTES")
)


test(
    "simple alternatives",
    [
        [
            Event(Fraction(0, 1), Fraction(1, 1), 'a'),
            Event(Fraction(1, 1), Fraction(2, 1), 'b'),
            Event(Fraction(2, 1), Fraction(3, 1), 'c')
        ]
    ],
    generate_events(parse_mini("<[a] [b] [c]>"), "NOTES")
)

test(
    "polyphony generation",
    [
        [
            Event(Fraction(0, 1), Fraction(1, 3), 'a'),
            Event(Fraction(1, 3), Fraction(2, 3), 'b'),
            Event(Fraction(2, 3), Fraction(1, 1), 'd'),
        ],
        [
            Event(Fraction(1, 3), Fraction(2, 3), 'c'),
            Event(Fraction(2, 3), Fraction(1, 1), 'e'),
        ],
        [
            Event(Fraction(1, 3), Fraction(2, 3), 'd'),
        ],
    ],
    generate_events(parse_mini("[a b,c,d d,e]"), "NOTES")
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
test_mini("one level one cycle", expected, notes("[A3 B3 C3]"))
expected = [[
    on("A3", 0), off("A3", 960), 
    on("B3", 960), off("B3", 960), 
    on("C3", 960), off("C3", 960), 
]]
test_mini("one level three cycles", expected, notes("<[A3] [B3] [C3]>"))
expected = [[
    on("A3", 0), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 320), 
    on("A3", 320), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 160), 
    on("D3", 160), off("D3", 160), 
]]
test_mini("three level nesting", expected, notes("[A3 B3 C3] [A3 B3 [C3 D3]]"))
expected = [[
    on("A3", 0), off("A3", 320), 
    on("B3", 320), off("B3", 320), 
    on("C3", 320), off("C3", 320), 
]]
test_mini("crazy whitespace", expected, notes(""" [ A3       B3 C3
          ] """))
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
test_mini("polyphony", expected, notes("[A3 B3,C3,D3 C3,E3]"))

expected = [[
    on("A3", 0), off("A3", 160), 
    on("B3", 480), off("B3", 160), 
    on("C3", 480), off("C3", 160), 
]]
test_mini("25% note width", expected, notes("[A3 B3 C3]").set_config("note_width", .25))

expected = [[
    on("A3", 384), off("A3", 192), 
    on("B3", 192), off("B3", 192), 
    on("C3", 192+384), off("C3", 192), 
]]
test_mini("rests", expected, notes("[~ A3 B3 ~ C3]"))

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
test_mini("polyphonic rests", expected, notes("[ E4,G4 ~ E4,G4 E4,G4 ]"))

expected = [
    [
        on("A3", 0, 0), off("A3", 320, 0), 
        on("B3", 320, 0), off("B3", 320, 0), 
        on("C3", 320, 0), off("C3", 320, 0), 
        on("A3", 320, 0), off("A3", 320, 0), 
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
test_mini("stacked cycles", expected, notes("[A3 B3 C3]").stack().notes("[A3 B3 C3 D3] [A4 B4 C4 D4]"))

expected = [[
    on("A3", 0, velocity=9), off("A3", 320, velocity=9), 
    on("B3", 320, velocity=9), off("B3", 320, velocity=9), 
    on("C3", 320, velocity=5), off("C3", 320, velocity=5), 
]]
test_mini("merged cycles", expected, notes("[A3 B3 C3]").velocity("[9 9 5]"))

expected = [[
    on("A3", 0, velocity=7), off("A3", 320, velocity=7), 
    on("B3", 320, velocity=7), off("B3", 320, velocity=7), 
    on("C3", 320, velocity=8), off("C3", 320, velocity=8), 
]]
test_mini("merged cycles: same length different rhythm", expected, notes("[A3 B3 C3]").velocity("[7 8]"))

expected = [[
    on("A3", 0, velocity=7), off("A3", 960, velocity=7), 
    on("B3", 960, velocity=8), off("B3", 960, velocity=8), 
    on("C3", 960, velocity=7), off("C3", 960, velocity=7), 
    on("A3", 960, velocity=8), off("A3", 960, velocity=8), 
    on("B3", 960, velocity=7), off("B3", 960, velocity=7), 
    on("C3", 960, velocity=8), off("C3", 960, velocity=8), 
]]
test_mini("merged cycles: different length same rhythm", expected, notes("[A3] [B3] [C3]").velocity("[7] [8]"))

expected = [
    [
        on("A3", 0, velocity=7), off("A3", 480, velocity=7), 
        on("C3", 480, velocity=9), off("C3", 480, velocity=9), 
    ],
    [
        on("B3", 0, 1, velocity=8), off("B3", 480, 1, velocity=8), 
    ]
]
test_mini("merged cycles: more voices in merger", expected, notes("[A3,B3 C3]").velocity("[7,8,9 9]"))

expected = [
    [
        on("A3", 0, velocity=7), off("A3", 480, velocity=7), 
        on("C3", 480, velocity=9), off("C3", 480, velocity=9), 
    ],
    [
        on("B3", 0, 1), off("B3", 480, 1), 
    ]
]
test_mini("merged cycles: more voices in mergee", expected, notes("[A3,B3 C3]").velocity("[7 9]"))

expected = [
    [
        on("A3", 0), off("A3", 480), 
        on("A3", 480), off("A3", 240), 
        on("A3", 240), off("A3", 240), 
        on("B3", 240), off("B3", 480), 
        on("B3", 480), off("B3", 240), 
        on("B3", 240), off("B3", 240), 
    ],
]
test_mini("rhythm: monophonic", expected, rhythm("[x [x x]]").notes("[A3] [B3]"))

expected = [
    [
        on("A3", 0), off("A3", 480), 
        on("A3", 480), off("A3", 240), 
        on("A3", 240), off("A3", 240), 
        on("B3", 240), off("B3", 480), 
        on("B3", 480), off("B3", 240), 
        on("B3", 240), off("B3", 240), 
    ],
    [
        on("C3", 0, 1), off("C3", 480, 1), 
        on("C3", 480, 1), off("C3", 240, 1), 
        on("C3", 240, 1), off("C3", 240, 1), 
        on("D3", 240, 1), off("D3", 480, 1), 
        on("D3", 480, 1), off("D3", 240, 1), 
        on("D3", 240, 1), off("D3", 240, 1), 
    ],
]
test_mini("rhythm: polyphonic", expected, rhythm("[x,x [x,x x,x]]").notes("[A3,C3] [B3,D3]"))

# expected:
# [[(57, 0, 0, 70), (57, 480, 0, 70), (57, 480, 0, 70), (57, 240, 0, 70), (57, 240, 0, 70), (57, 240, 0, 70), (59, 240, 0, 70), (59, 480, 0, 70), (59, 480, 0, 70), (59, 240, 0, 70), (59, 240, 0, 70), (59, 240, 0, 70)], 
#  [(59, 0, 0, 70), (59, 480, 0, 70), (59, 480, 0, 70), (59, 240, 0, 70), (59, 240, 0, 70), (59, 240, 0, 70), (50, 240, 0, 70), (50, 480, 0, 70), (50, 480, 0, 70), (50, 240, 0, 70), (50, 240, 0, 70), (50, 240, 0, 70)]]

# actual:
# [[(57, 0, 0, 70), (57, 480, 0, 70), (57, 480, 0, 70), (57, 240, 0, 70), (57, 240, 0, 70), (57, 240, 0, 70), (59, 240, 0, 70), (59, 480, 0, 70), (59, 480, 0, 70), (59, 240, 0, 70), (59, 240, 0, 70), (59, 240, 0, 70)],
#  [(48, 0, 1, 70), (48, 480, 1, 70), (48, 480, 1, 70), (48, 240, 1, 70), (48, 240, 1, 70), (48, 240, 1, 70), (50, 240, 1, 70), (50, 480, 1, 70), (50, 480, 1, 70), (50, 240, 1, 70), (50, 240, 1, 70), (50, 240, 1, 70)]]
