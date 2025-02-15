from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key, print_ascii
oct = "oct"
second = "2nd"
third = "3rd"
fourth = "4th"
fifth = "5th"
sixth = "6th"
seventh = "7th"

"""
Used for Jangles & Thumps: https://write.fawm.org/songs/306794
"""

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def spread_notes(b0, t0, t1, s0, s1):
    return (
        b0, 
        t0 + oct, 
        t1 + oct, 
        s0 + oct + oct, 
        s1 + oct + oct,
    )

def pattern_a(b0, t0, t1, s0, s1):
    (b0, t0, t1, s0, s1) = spread_notes(b0, t0, t1, s0, s1)

    return f"""
{s0:3} {s1:3} {s0:3} {s1:3} {s0:3} {s1:3} {s0:3} {s1:3}
{t0:3} === === {t0:3} {t1:3} === === ===
{b0:3} === === === === === === ===
"""

def pattern_b(b0, t0, t1, s0, s1):
    (b0, t0, t1, s0, s1) = spread_notes(b0, t0, t1, s0, s1)

    return f"""
{s0:3} === --- {s0:3} {s1:3} === --- ---
{t0:3} === --- {t0:3} {t1:3} --- {t1:3} ---
{b0:3} === --- {b0:3} {b0:3} === --- ---
"""

def pattern_c(b0, t0, t1, s0, s1):
    (b0, t0, t1, s0, s1) = spread_notes(b0, t0, t1, s0, s1)

    return f"""
{s0:3} === --- {s0:3} {s1:3} {s1:3} {s1:3} {s1:3}
{t0:3} === --- {t0:3} {t1:3} === --- ---
{b0:3} === --- {b0:3} {b0:3} === --- ---
"""

def song():
    """
    D F#m C#m Bm
    D F#m C#m A
    """
    i = Note("A1", "A major")
    ii = i + second # B
    iii = i + third # C#
    iv = i + fourth # D
    v = i + fifth # E
    vi = i + sixth # F#
    vii = i + seventh # G#

    a_section = [
        pattern_a(iv, i, vi, iv, vi), # D
        pattern_a(vi, i, vi, iii, vi), # F#m
        pattern_a(iii, vii, v, v, vii), # C#m
        pattern_a(ii, iv, ii, vi, iv), # Bm

        pattern_a(iv, i, vi, iv, vi), # D
        pattern_a(vi, i, vi, iii, vi), # F#m
        pattern_a(iii, vii, v, v, vii), # C#m
        pattern_a(i, iii, i, i+oct, v), # A
    ]
    b_section = [
        pattern_b(iv, i, vi, iv, vi), # D
        pattern_c(vi, i, vi, iii, vi), # F#m
        pattern_b(iii, vii, v, v, vii), # C#m
        pattern_c(ii, iv, ii, vi, iv), # Bm

        pattern_b(iv, i, vi, iv, vi), # D
        pattern_c(vi, i, vi, iii, vi), # F#m
        pattern_b(iii, vii, v, v, vii), # C#m
        pattern_c(i, iii, i, i+oct, v), # A
    ]

    bars = a_section + a_section + a_section + b_section + b_section + a_section

    print_ascii(bars)

    return make_lines(bars)

play(song(), Config(beats_per_minute=87, symbols_per_beat=2))
#play(song(), Config(beats_per_minute=87, symbols_per_beat=2, midi_device='IAC Driver Bus 1'))

#play([TUNING], Config(beats_per_minute=10, loops=10))


