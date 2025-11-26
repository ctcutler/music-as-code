from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def interval_by_letter(p0, p1, l):
    top_voice = ""
    bottom_voice = ""
    for i in range(7, -1, -1):
        if i > 3:
            top_voice += f"{p1:3} === " if ord(l) >> i & 1 else "--- --- "
        else:
            bottom_voice += f"{p0:3} === " if ord(l) >> i & 1 else "--- --- "

    return stack(top_voice, bottom_voice)

def interval(p0, p1):
    return f"""
{p1:3} === === === === === === ===  === === === === === === --- ---
{p0:3} === === === === === === ===  === === === === === === --- ---
"""

def song():
    i = Note("A1", "A minor")
    mii = i + "m2"
    iii = i + "3rd"
    iv = i + "4th"
    v = i + "5th"
    vi = i + "6th"
    vii = i + "7th"
    bars = [
        interval_by_letter(i, v, 'L'),
        interval_by_letter(iii, vii, 'O'),
        interval_by_letter(vii-"8th", iv, 'V'),
        interval_by_letter(mii, vi, 'E'),
    ]
    return make_lines(bars*100)

play(song(), Config(beats_per_minute=105))

#play([TUNING], Config(beats_per_minute=10, loops=10))


n = "Matthew Klooster"
