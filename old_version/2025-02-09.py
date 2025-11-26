from asciimidi import play, Config
from note_util import stack, make_lines, Note, set_key, print_ascii, m3, P4, P5, M6, m7

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""


def solo():
    return f"""
{p0:3} {p1:3} {p2:3} {p3:3} {p4:3} {p4:3} {p3:3} {p4}
"""

def rhythm(r):
    p0 = r
    p1 = r + P5
    p2 = r + M6 
    p3 = r + m7

    return f"""
{p1:3} {p1:3} {p2:3} {p2:3} {p3:3} {p3:3} {p2:3} {p2:3}
{p0:3} {p0:3} {p0:3} {p0:3} {p0:3} {p0:3} {p0:3} {p0:3}
"""

def song():
    i = Note("A1", "A minor")
    iii = i + m3
    iv = i + P4
    v = i + P5
    vii = i + m7

    bars = [
        rhythm(i),
        rhythm(i),
        rhythm(i),
        rhythm(i),
        rhythm(iv),
        rhythm(iv),
        rhythm(i),
        rhythm(i),
        rhythm(v),
        rhythm(iv),
        rhythm(i),
        rhythm(v),
    ]
    print_ascii(bars)

    return make_lines(bars*100)

#play(song(), Config(beats_per_minute=116, symbols_per_beat=4))
play(song(), Config(beats_per_minute=98, swing=.6, midi_device='IAC Driver Bus 1'))

#play([TUNING], Config(beats_per_minute=10, loops=10))


