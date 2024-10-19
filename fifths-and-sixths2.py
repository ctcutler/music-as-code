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


KEY = "C"
MODE = "major"
def fifth(note):
    return [note, scale_interval(KEY, MODE, note, 5)]

def sixth(note):
    return [note, scale_interval(KEY, MODE, note, 6)]

def rest_layer():
    return "--- --- --- --- --- --- --- ---"

def interval_layer(p1, p2):
    return  f"{p1:3} === --- --- {p2:3} === --- ---"

def interval_stack(i1, i2, j1, j2):
    return f"""
    --- --- --- --- {j2:3} --- {j2:3} ---   --- {j2:3} --- {j2:3} --- --- --- {j2:3}
    --- --- --- --- {j1:3} --- {j1:3} ---   --- {j1:3} --- {j1:3} --- --- --- {j1:3}
    {i2:3} --- {i2:3} --- --- --- --- ---   {i2:3} === === === --- --- --- {i2:3}
    {i1:3} --- {i1:3} --- --- --- --- ---   {i1:3} === === === --- --- --- {i1:3}
    """
    

def song3():
    return [
        concat([
            interval_stack(*(fifth("C2") + sixth("E2"))),
            interval_stack(*(sixth("B1") + fifth("G1"))),
        ]),
        concat([
            interval_stack(*(fifth("A1") + fifth("F1"))),
            interval_stack(*(sixth("G1") + fifth("G1"))),
        ]),
        concat([
            interval_stack(*(fifth("C2") + sixth("E2"))),
            interval_stack(*(fifth("F2") + fifth("E2"))),
        ]),
        concat([
            interval_stack(*(fifth("F2") + sixth("D2"))),
            interval_stack(*(sixth("B1") + fifth("C2"))),
        ])
    ]

def make_lines(bars):
    return [
        concat(bars[i:i+4]) for i in range(0, len(bars), 4)
    ]

def song4():
    """
    # commit to a rhythm (3-3-2) and a simpler set of chords from stacked fifths and sixths like in that piano piece
    # build complexity every repeat, and then let it drain away to a different place
    # serene
    # Am G F Em / Am G Em F ... Am

    --- --- --- {p4:3} --- --- {p4:3} ---
    --- --- --- {p3:3} --- --- {p3:3} ---
    {p2:3} === === === === === === ===
    {p1:3} === === === === === === ===
    """

    bars = []
    fifths = ["A1", "G1", "F1", "E1", "A1", "G1", "E1", "F1"]
    sixths = ["C2", "B1", "A1", "G1", "C2", "B1", "G1", "A1"]
    for i in range(len(fifths)):
        p1, p2 = fifth(fifths[i])
        p3, p4 = sixth(sixths[i])
        base_rhythm = f"""
{p4:3} --- --- {p4:3} --- --- {p4:3} ---
{p3:3} --- --- {p3:3} --- --- {p3:3} ---
{p2:3} --- --- {p2:3} --- --- {p2:3} ---
{p1:3} --- --- {p1:3} --- --- {p1:3} ---
        """
        bars.append(base_rhythm)
    return make_lines(bars)

def song5():
    """
    Dunno yet.
    If I'm gonna go major (And I think I should, minor is sounding gloomy), get a seventh
    chord in there.

    OK, this piece is called "start at zero"
    And it is not serene, it is uplifting, though that word troubles me so maybe there's
    better one.  But that, at least, is the direction I want to go.

    Play with those 6/8 rhythms.

    create a note object such that I can do:
    n1 = n("A1") (figures out key from context?
    n1 + 1 (1 step)
    n1 + M3 (key agnostic, literally 4 steps)
    n1 + third (third in key)
    f"{n1:3} (works as expected)
    """
    bars = []
    fifths = [fifth("C2"), fifth("A1"), fifth("G1"), fifth("F1")]
    sixths = [sixth("E2"), sixth("C3"), sixth("B3"), sixth("A4")]

    # bass only
    for (p1, p2) in fifths:
        bars.append(f"""
--- --- --- --- --- --- --- ---
--- --- --- --- --- --- --- ---
{p2:3} === === === === === === ===
{p1:3} === === === === === === ===
        """)

    # w/plinks
    for i in range(len(fifths)):
        p1, p2 = fifths[i]
        p3, p4 = sixths[i]
        if i % 2:
            bars.append(f"""
--- --- {p4:3} --- --- --- {p4:3} ---
--- --- {p3:3} --- --- --- {p3:3} ---
{p2:3} === === === === === === ===
{p1:3} === === === === === === ===
            """)
        else:
            bars.append(f"""
{p4:3} --- --- --- {p4:3} --- --- ---
{p3:3} --- --- --- {p3:3} --- --- ---
{p2:3} === === === === === === ===
{p1:3} === === === === === === ===
            """)


    return make_lines(bars)
        
config = Config(note_width=.5, loops=1, beats_per_minute=77)
play(song5(), config)

tuning = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""
#play([tuning], Config(beats_per_minute=10, loops=10))
