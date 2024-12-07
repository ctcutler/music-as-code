from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def pattern(p0, p1, p2):
    b0 = p0 - "P8" - "P8" - "P8"
    return f"""
{p0:3} === {p1:3} === {p2:3} === --- --- {p0:3} {p1:3} === --- {p2:3} === --- ---
--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
{b0:3} === === === {b0:3} === === === {b0:3} === === === {b0:3} === === ===
"""

def song():
    i = Note("C4", "C major")

    bars = [
        pattern(i, i+"3rd", i+"5th"),
        pattern(i-"2nd", i+"3rd", i+"5th"),
    ]
    return make_lines(bars*100)

play(song(), Config(beats_per_minute=105, symbols_per_beat=4))

#play([TUNING], Config(beats_per_minute=10, loops=10))


