from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def pattern(p0, p1):
    return f"""
--- --- C0  --- C0  C0  --- ---
--- --- C0  --- --- C0  --- C0 
{p1:3} === === === === === === ===
{p0:3} === === === === === === ===
"""

def song():
    i = Note("A2", "A minor")

    bars = [
        pattern(i, i+"5th"), # Am
        pattern(i-"3rd", i+"3rd"), # F
        pattern(i-"2nd", i+"5th"), # G6
        pattern(i-"2nd", i+"4th"), # G
    ]
    return make_lines(bars*100)

play(song(), Config(beats_per_minute=68))

#play([TUNING], Config(beats_per_minute=10, loops=10))


