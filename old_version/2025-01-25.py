from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key, print_ascii
oct = "oct"
second = "2nd"
third = "3rd"
fourth = "4th"
fifth = "5th"
sixth = "6th"
seventh = "7th"

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""


# C G C A C G A/G F

def pattern(b0, b1, t0, t1):
    return f"""
{t0:3} --- {t0:3} --- {t0:3} === === === {t0:3} {t1:3} {t0:3} {t1:3} {t0:3} === --- ---
{b0:3} === === {b0:3} {b0:3} === === === {b1:3} === === {b1:3} {b1:3} === === === 
"""

def song():
    i = Note("C#2", "C# minor")
    iii = i + third
    iv = i + fourth
    v = i + fifth
    vi = i + sixth
    tenor_i = i + oct
    tenor_ii = tenor_i + second
    tenor_vi = tenor_i - third
    tenor_v = tenor_i - fourth
    tenor_iii = tenor_i + third
    tenor_iv = tenor_i + fourth

    bars = [
        pattern(i, v, tenor_i, tenor_ii),
        pattern(i, vi, tenor_vi, tenor_v),
        pattern(i, v, tenor_i, tenor_ii),
        pattern(iv, iii, tenor_iii, tenor_iv),
    ]

    print_ascii(bars)

    return make_lines(bars*100)

play(song(), Config(beats_per_minute=77, symbols_per_beat=4))

#play([TUNING], Config(beats_per_minute=10, loops=10))


