from asciimidi import play, Config
from note_util import stack, concat, make_lines, n, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

def chord_bar(c0, c1, c2):
    return f"""
{c0[3]:3} === === --- {c1[3]:3} --- {c2[3]:3} ===
{c0[1]:3} === === --- {c1[2]:3} --- {c2[2]:3} ===
{c0[2]:3} === === --- {c1[1]:3} --- {c2[1]:3} ===
{c0[0]:3} === === --- {c1[0]:3} --- {c2[0]:3} ===
"""

def eighths_bar(i0, i1):
    return f"""
{i0[1]:3} {i0[1]:3} {i0[1]:3} {i1[1]:3} {i1[1]:3} {i1[1]:3}
{i0[0]:3} {i0[0]:3} {i0[0]:3} {i1[0]:3} {i1[0]:3} {i1[0]:3}
"""

def bass_bar(p0, p1):
    return f"""
{p0-14:3} --- {p0-14:3} {p1-14:3} --- {p1-14:3}
"""

def song2():
    i = n("C3", "C major")
    iv = i+3
    v = i+4
    vi = i-2
    return make_lines([
        stack([
            eighths_bar((i, i+4), (i, i+6)),
            bass_bar(i, v)
        ]),
        stack([
            eighths_bar((iv, iv+4), (iv, iv+3)),
            bass_bar(iv, iv)
        ]),
        stack([
            eighths_bar((vi, vi+4), (vi, vi+5)),
            bass_bar(vi, vi)
        ]),
        stack([
            eighths_bar((v, v+4), (v, v+6)),
            bass_bar(v, v)
        ]),
    ]*8)


def song1():
    i = n("C3", "C major")
    ii = i+1
    iii = i+2
    iv = i+3
    v = i+4
    vi = i+5
    vii = i+6

    I = [i, i+2, i+4, i+7]
    I7 = [i, i+2, i+4, i+"m7"]
    III = [iii, iii+2, iii+4, iii+7]
    VI = [vi, vi+2, vi+4, vi+7]
    IV = [iv, iv+2, iv+4, iv+7]
    V = [v, v+2, v+4, v+7]
    V7 = [v, v+2, v+4, v+6]

    return make_lines([
        chord_bar(I, I, I7),
        chord_bar(VI, VI, VI),
        chord_bar(III, III, III),
        chord_bar(V, V, V7),
    ] * 8)

def intro(i):
    return f"""
--- --- --- --- --- --- --- {i:3}
"""

def figure(i, form="first", leadin=None):
    iii = i + 2
    v = i + 4
    vi = i + 5
    vii = i + 6

    leadin = i if leadin is None else leadin

    forms = {
        "first": f"""
{vii:3} {v:3} === {iii:3} {v:3} === {vii:3} {leadin:3}
""",
        "second": f"""
{vii:3} {v:3} === {iii:3} {v:3} === --- {leadin:3}
""",
        "last": f"""
{vii:3} {v:3} === {iii:3} {v:3} === --- ---
""",
        "first_alt": f"""
{vii:3} {v:3} === {iii:3} {v:3} === {vi:3} {leadin:3}
"""
    }

    assert form in forms, f"unexpected form {form}"

    return forms[form]

def outro(i):
    return figure(i, form="last")

def bass(i):
    return f"""
{i-14:3} === === === === === === ===
"""

def song3():
    i = n("C3", "C major")
    iv = i + 3
    return make_lines(
        stack(
            intro(i),
            bass(i),
        ),
        [
            stack(
                figure(i, form="first"), 
                bass(i)
            ),
            stack(
                figure(i, form="second", leadin=iv),
                bass(i)
            ),
            stack(
                figure(iv, form="first_alt"), 
                bass(iv)
            ),
            stack(
                figure(iv, form="second", leadin=i),
                bass(iv)
            ),
        ] * 4,
        stack(
            figure(i, form="first"), 
            bass(i),
        ),
        stack(
            outro(i),
            bass(i),
        ),
    )

play(song3(), Config(beats_per_minute=72, note_width=.5))

#play([TUNING], Config(beats_per_minute=10, loops=10))
