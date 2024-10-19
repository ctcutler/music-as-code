from asciimidi import play, Config
from note_util import stack, concat, make_lines, n, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

"""
- adding 3-5 bounce
"""

def figure_a(i, note_5, leadin=None):
    if not leadin: leadin = "==="
    iii = i + 2
    v = i + 4
    vii = i + 6

    return f"""
{vii:3} === {v:3} === === === {iii:3} === {v:3} === === === {note_5:3} === === {leadin:3}
"""

def figure_b(i):
    iii = i + 2
    v = i + 4
    vii = i + 6

    return f"""
{vii:3} === {v:3} === === === {iii:3} === {v:3} === === === --- --- --- ---
"""

def rest(leadin):
    return f"""
--- --- --- --- --- --- --- {leadin:3}
"""

def tied_note(leadin=None):
    if not leadin: leadin = "==="
    return f"""
=== === === === === === === {leadin:3}
"""


def bass(p0, p1=None):
    p0 -= 14
    p1 = "===" if p1 is None else p1 - 14
    return f"""
{p0:3} === === === {p1:3} === === ===
"""


def song():
    i = n("C3", "C major")
    iv = i + 3
    vii = i + 6
    return make_lines(
        rest(i), 

        # I
        figure_a(i, note_5=vii),
        rest(leadin=i), 
        figure_b(i),
        rest(leadin=i), 

        figure_a(i, note_5=vii),
        tied_note(leadin=i), 
        figure_b(i),
        rest(leadin=iv), 

        # IV -> I
        figure_a(iv, note_5=iv+5),
        rest(leadin=iv), 
        figure_b(iv),
        rest(leadin=iv), 

        figure_a(iv, note_5=iv+5, leadin=i),
        figure_b(i), 
        rest(leadin=i), 
        figure_b(i), 
    )

play(song(), Config(beats_per_minute=92, note_width=.5, symbols_per_beat=4))

#play([TUNING], Config(beats_per_minute=10, loops=10))
