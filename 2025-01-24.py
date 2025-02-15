from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key, print_ascii
oct = "oct"
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

def pattern(b, t0, t1, t2, t3, s0, s1, s2):
    return f"""
{s0:3} {s1:3} {s2:3} === {s2:3} === {s0:3} {s1:3} {s2:3} === {s2:3} === {s2:3} === {s2:3} ===
{t0:3} === {t3:3} === {t0:3} === {t2:3} === {t0:3} === {t1:3} === {t0:3} === {t1:3} ===
{b:3} === === === {b:3} === === === {b:3} === === === {b:3} === === ===
"""

def song():
    i = Note("A2", "A minor")
    iii = i + third
    iv = i + fourth
    v = i + fifth
    vi = i + sixth
    accent_i = i + oct + oct 
    accent_iii = accent_i + third
    accent_iv = accent_i + fourth
    accent_v = accent_i + fifth
    accent_vi = accent_i + sixth
    accent_vii = accent_i + seventh
    accent_viii = accent_i + oct

    bars = [
        pattern(i, i, iii, iv, v, accent_iii, accent_iv, accent_v),
        pattern(vi-oct, i, iii, v, vi, accent_iv, accent_v, accent_vi),
    ]

    print_ascii(bars)

    return make_lines(bars*100)

play(song(), Config(beats_per_minute=104, symbols_per_beat=4))

#play([TUNING], Config(beats_per_minute=10, loops=10))


