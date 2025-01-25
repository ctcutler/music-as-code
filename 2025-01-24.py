from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key, print_ascii
oct = "oct"
third = "3rd"
fourth = "4th"
fifth = "5th"
sixth = "6th"

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""
#{p5:3} === {p5:3} === {p5:3} === {p5:3} === {p5:3} {p5:3} {p5:3} === {p5:3} === {p5:3} === 

def pattern(p0, p1, p2, p3, p4, p5):
    return f"""
{p5:3} {p5:3} {p5:3} === {p5:3} === {p5:3} {p5:3} {p5:3} === {p5:3} === {p5:3} === {p5:3} ===
{p1:3} === {p4:3} === {p1:3} === {p3:3} === {p1:3} === {p2:3} === {p1:3} === {p2:3} ===
{p0:3} === === === {p0:3} === === === {p0:3} === === === {p0:3} === === ===
"""

def song():
    i = Note("A2", "A minor")
    iii = i + third
    iv = i + fourth
    v = i + fifth
    vi = i + sixth
    accent_i = i + oct + oct

    bars = [
        pattern(i, i, iii, iv, v, accent_i),
        pattern(i, i, iii, v, vi, accent_i),
    ]

    print_ascii(bars)

    return make_lines(bars*100)

play(song(), Config(beats_per_minute=104, symbols_per_beat=4))

#play([TUNING], Config(beats_per_minute=10, loops=10))


