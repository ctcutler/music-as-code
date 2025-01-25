from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key
oct = "oct"
third = "3rd"
fourth = "4th"
fifth = "5th"

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def pattern(p0, p1, p2, p3):
    return f"""
{p3:3} === {p3:3} {p3:3} === {p3:3} {p3:3} ===
{p2:3} === === {p2:3} === === {p2:3} ===
{p0:3} {p1:3} {p1:3} {p0:3} {p1:3} {p1:3} {p0:3} {p1:3}
"""

def song():
    vi = Note("E2", "E minor")
    i = vi + third
    ii = vi + fourth
    iii = vi + fifth
    bars = [
        pattern(vi, vi+fifth, vi+oct, vi+oct+fifth),
        pattern(ii, ii+fifth, ii+oct, ii+oct+fifth),
        pattern(vi, vi+fifth, vi+oct, vi+oct+fifth),
        pattern(iii, iii+fifth, iii+oct, iii+oct+fifth),
        pattern(i, i+fifth, i+oct, i+oct+fifth),
        pattern(vi, vi+fifth, vi+oct, vi+oct+fifth),
    ]

    return make_lines(bars*100)

play(song(), Config(beats_per_minute=78))

#play([TUNING], Config(beats_per_minute=10, loops=10))


