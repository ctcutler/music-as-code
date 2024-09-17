from asciimidi import play, Config
from note_util import stack, concat, make_lines, n, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

def shuffle_bar(p0, p1, p2, p3):
    return f"{p1:3} {p0:3} {p2:3} {p0:3} {p3:3} {p0:3} {p2:3} {p0:3}"

def horn_bar(p0, p1):
    return f"""
{p1:3} --- {p1:3} {p0:3} --- {p1:3} === ---
{p0:3} --- {p0:3} {p0:3} --- {p0:3} === ---
"""

def song2():
    set_key("A minor")
    i_bass = [shuffle_bar(n("A0"), n("E1"), n("F#1"), n("G1"))]
    iv_bass = [shuffle_bar(n("D1"), n("A1"), n("B1"), n("C2"))]
    v_bass = [shuffle_bar(n("E1"), n("B1"), n("C#2"), n("D2"))]

    i_horn = [horn_bar(n("A3"), n("G4"))]
    iv_horn = [horn_bar(n("D3"), n("C4"))]
    v_horn = [horn_bar(n("E3"), n("B4"))]

    i_bar = [stack(i_horn + i_bass)]
    iv_bar = [stack(iv_horn + iv_bass)]
    v_bar = [stack(v_horn + v_bass)]
    print(i_bar)

    bars = i_bar * 4 +\
        iv_bar * 2 + i_bar * 2 +\
        v_bar + iv_bar + i_bar * 2

    return make_lines(bars * 4)

play(song2(), Config(beats_per_minute=92, note_width=.75, swing=.7))

#play([TUNING], Config(beats_per_minute=10, loops=10))
