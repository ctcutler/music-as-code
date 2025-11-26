from asciimidi import play, Config
from note_util import stack, make_lines, Note, set_key, print_ascii, second, third, fifth, seventh, oct

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def bass(b0):
    return f"""
{b0:3} --- --- --- --- --- --- --- --- --- --- --- {b0:3} --- --- ---
"""

def strum_a(p0, p1, p2):
    return f"""
{p0:3} {p1:3} {p2:3} {p1:3} {p2:3} --- --- --- --- --- --- --- --- --- --- ---
"""

def strum_b(p0, p1, p2):
    return f"""
{p2:3} {p1:3} --- {p0} --- {p0:3} --- --- --- --- --- --- --- --- --- ---
"""

def strum_c(p0, p1, p2):
    return f"""
{p0:3} {p2:3} {p0:3} {p1:3} {p0:3} {p1:3} {p2:3} --- --- --- --- --- --- --- --- ---
"""

def bar_a(b0, p0, p1, p2):
    return stack(
        strum_a(p0, p1, p2),
        bass(b0), 
    )

def bar_b(b0, p0, p1, p2):
    return stack(
        strum_b(p0, p1, p2),
        bass(b0), 
    )

def bar_c(b0, p0, p1, p2):
    return stack(
        strum_c(p0, p1, p2),
        bass(b0), 
    )

def song():
    """
    ok 16th note sweeps, somewhat overlapping
    let's make this two handed
    if I make a very small note length then only the held notes will stick around
    hmmmm, though really I think I wan tto do this all wiht triggers
    so maybe 2 voices of sweeps and 1 bassline

    yeah, strums
    """
    i = Note("A1", "A major")
    iii = i + third
    ii = i + second
    Csm7 = [iii, iii+third, iii+seventh]
    Csm = [iii, iii+third, iii+fifth]
    Bm = [ii, ii+third, ii+fifth]
    Bm7 = [ii, ii+third, ii+seventh]

    bars = [
        bar_a(ii-oct+seventh, *Bm7),
        bar_c(iii-oct+seventh, *Csm7),
        bar_a(iii-oct+fifth, *Csm),
        bar_b(ii-oct+fifth, *Bm),
    ]
    print_ascii(bars)

    return make_lines(bars*100)

#play(song(), Config(beats_per_minute=116, symbols_per_beat=4))
play(song(), Config(beats_per_minute=98, symbols_per_beat=4, midi_device='IAC Driver Bus 1'))

#play([TUNING], Config(beats_per_minute=10, loops=10))


