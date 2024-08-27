from asciimidi import play, Config, stack, concat, scale_note, scale_interval

"""
Things to try:
- more patterns
  - a smoother one
  - a different rhythm
- mid-measure chord changes
"""

def rest_layer():
    return "--- --- --- --- --- --- --- ---"

def bass_layer(p):
    return  f"{p:3} === === === === === === ---"

def rhythm_layer1(p1, p2, p3):
    return  f"{p1:3} --- --- {p2:3} --- --- {p3:3} ---"

def rhythm_layer2(p1, p2, p3):
    return  f"{p1:3} --- --- --- --- --- {p3:3} ---"

def rhythm_layer3(p1, p2, p3):
    return  f"{p1:3} --- {p2:3} --- --- --- {p3:3} ---"

def rhythm_stack1(b, s1, s2, f1, f2, l1, l2):
    return stack([
        rhythm_layer1(s1, f1, f1), 
        rhythm_layer3(s2, f2, f2), 
        rest_layer(),
        bass_layer(b)
    ])

def rhythm_stack2(b, s1, s2, f1, f2, l1, l2):
    return stack([
        rhythm_layer2(s1, f1, f1), 
        rhythm_layer2(s2, f2, f2), 
        rhythm_layer1(l2, l1, l1), 
        bass_layer(b)
    ])

def line_wrap(stacks):
    return [concat(stacks[i:i+4]) for i in range(0, len(stacks), 4)]

def song2():
    key = "C"
    mode = "major"
    degree_sequence = ["VI", "IV", "I", "V", "VI", "IV", "V", "I"]
    part1 = []
    part2 = []

    for degree in degree_sequence:
        bass = scale_note(key, mode, degree, octave=2)
        fifth1 = scale_note(key, mode, degree, octave=3)
        fifth2 = scale_interval(key, mode, fifth1, 5)
        sixth1 = scale_interval(key, mode, fifth1, 3)
        sixth2 = scale_interval(key, mode, sixth1, 6)
        lead1 = scale_interval(key, mode, scale_note(key, mode, degree, octave=2), 5)
        lead2 = scale_interval(key, mode, scale_note(key, mode, degree, octave=2), 8)

        part1.append(rhythm_stack1(bass, fifth1, fifth2, sixth1, sixth2, lead1, lead2))
        part2.append(rhythm_stack2(bass, fifth1, fifth2, sixth1, sixth2, lead1, lead2))

    return line_wrap(part1+part2)

def song():

    A = ("A2", "C3", "A3", "A3", "E4")
    F = ("F2", "A3", "F3", "F3", "C4")
    C = ("C2", "E3", "C3", "C3", "G4")
    G = ("G2", "B3", "G3", "G3", "D4")
    chords1 = [ A, F, C, G ]
    chords2 = [ A, F, G, C ]

    return [
        concat([ bass_stack(chord[0]) for chord in chords1 ]),
        concat([ bass_stack(chord[0]) for chord in chords2 ]),

        concat([ rhythm_stack1(*chord) for chord in chords1 ]),
        concat([ rhythm_stack2(*chord) for chord in chords2 ]),

        concat([ rhythm_stack3(*chord) for chord in chords1 ]),
        concat([ rhythm_stack1(*chord) for chord in chords2 ]),

        concat([ rhythm_stack2(*chord) for chord in chords1 ]),
        concat([ rhythm_stack3(*chord) for chord in chords2 ]),
    ]
        
config = Config(note_width=.5, loops=10, beats_per_minute=112)
play(song2(), config)

tuning = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""
#play([tuning], Config(beats_per_minute=10, loops=10))
