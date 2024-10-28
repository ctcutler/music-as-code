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

def rest(leadin=None):
    leadin = "---" if leadin == None else leadin
    return f"""
--- --- --- --- --- --- --- {leadin:3}
"""

def tied_note(leadin=None):
    if not leadin: leadin = "==="
    return f"""
=== === === === === === === {leadin:3}
"""


def bass(p0):
    p0 -= 14
    return f"""
{p0:3} === === === === === === === === === === === === === === ===
"""

def bass_4(p0):
    p0 -= 14
    return f"""
{p0:3} === === === === === === ===
"""


def song():
    i = n("C3", "C major")
    ii = i + 1
    iii = i + 2
    iv = i + 3
    v = i + 4
    vii = i + 6
    return make_lines(
        stack(
            rest(i), 
            rest(),
        ),

        [
            # I
            stack(
                figure_a(i, note_5=vii),
                bass(i),
            ),
            stack(
                rest(leadin=i), 
                rest(),
            ),
            stack(
                figure_b(i),
                bass(iii),
            ),
            stack(
                rest(leadin=i), 
                rest(),
            ),

            stack(
                figure_a(i, note_5=vii),
                bass(i),
            ),
            stack(
                tied_note(leadin=i), 
                rest(),
            ),
            stack(
                figure_b(i),
                bass(iii),
            ),
            stack(
                rest(leadin=iv), 
                rest(),
            ),

            # IV -> I
            stack(
                figure_a(iv, note_5=iv+5),
                bass(iv),
            ),
            stack(
                rest(leadin=iv), 
                rest(),
            ),
            stack(
                figure_b(iv),
                bass(ii),
            ),
            stack(
                rest(leadin=iv), 
                rest(),
            ),

            stack(
                figure_a(iv, note_5=iv+5, leadin=i),
                bass(iv),
            ),
            stack(
                figure_b(i), 
                bass(i),
            ),
            stack(
                rest(leadin=i), 
                rest(),
            ),
        ],
        stack(
            figure_b(i), 
            bass(i)
        )
    )

play(song(), Config(beats_per_minute=92, note_width=.5, symbols_per_beat=4))

#play([TUNING], Config(beats_per_minute=10, loops=10))
