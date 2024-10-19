from asciimidi import play, Config
from note_util import stack, concat, make_lines, n, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""


"""
Next: 

root sixteenth leading into the next measure
whole note rest or tied end note at end at first but then start running the phrases together in the middle then space them out again at the end

drop the leadin entirely when teh phrases are close together sometimes

bounce back and forth between 3rd and 5th at end of the phrase

thnk about the phrases as two bars long where sometimes the second bar is a held note or a rest
"""


def figure(i, form="first_7", leadin=None):
    iii = i + 2
    v = i + 4
    vi = i + 5
    vii = i + 6

    leadin = i if leadin is None else leadin

    forms = {
        # X X = X   X = X X
        "first_7": f"""
{vii:3} {v:3} === {iii:3} {v:3} === {vii:3} {leadin:3}
""",
        "first_6": f"""
{vii:3} {v:3} === {iii:3} {v:3} === {vi:3} {leadin:3}
""",
        "second": f"""
{vii:3} {v:3} === {iii:3} {v:3} === --- {leadin:3}
""",
        "last": f"""
{vii:3} {v:3} === {v:3} {i:3} === --- ---
""",
        # X X = -   X = - X
        "first_7_a": f"""
{vii:3} {v:3} === --- {v:3} === --- {leadin:3}
""",
        "first_6_a": f"""
{vii:3} {v:3} === --- {v:3} === --- {leadin:3}
""",
        "second_a": f"""
{vii:3} {v:3} === --- {v:3} === --- {leadin:3}
""",
        # X X = X   - - X X
        "first_7_b": f"""
{vii:3} {v:3} === {iii:3} --- --- {vii:3} {leadin:3}
""",
        "first_6_b": f"""
{vii:3} {v:3} === {iii:3} --- --- {vi:3} {leadin:3}
""",
        "second_b": f"""
{vii:3} {v:3} === {iii:3} --- --- --- {leadin:3}
""",
        # X - - X   X = X X
        "first_7_c": f"""
{vii:3} --- --- {iii:3} {v:3} === {vii:3} {leadin:3}
""",
        "first_6_c": f"""
{vii:3} --- --- {iii:3} {v:3} === {vi:3} {leadin:3}
""",
        "second_c": f"""
{vii:3} --- --- {iii:3} {v:3} === --- {leadin:3}
""",
    }

    assert form in forms, f"unexpected form {form}"

    return forms[form]

def intro(i):
    return f"""
--- --- --- --- --- --- --- {i:3}
"""

def bass(p0, p1=None):
    p0 -= 14
    p1 = "===" if p1 is None else p1 - 14
    return f"""
{p0:3} === === === {p1:3} === === ===
"""

def rest():
    return """
--- --- --- --- --- --- --- ---
"""

def song3():
    i = n("C3", "C major")
    iii = i + 2
    iv = i + 3
    v = i + 4
    vi = i + 5
    return make_lines(
        stack(
            intro(i),
            rest(),
        ),
        stack(
            figure(i, form="first_7_a"), 
            bass(i)
        ),
        stack(
            figure(i, form="second_a", leadin=iv),
            bass(iii)
        ),
        stack(
            figure(iv, form="first_6_a"), 
            bass(iv)
        ),
        stack(
            figure(iv, form="second_a", leadin=i),
            bass(vi, v)
        ),
        stack(
            figure(i, form="first_7_b"), 
            bass(i)
        ),
        stack(
            figure(i, form="second_b", leadin=iv),
            bass(iii)
        ),
        stack(
            figure(iv, form="first_6_b"), 
            bass(iv)
        ),
        stack(
            figure(iv, form="second_b", leadin=i),
            bass(vi, v)
        ),
        stack(
            figure(i, form="first_7_c"), 
            bass(i)
        ),
        stack(
            figure(i, form="second_c", leadin=iv),
            bass(iii)
        ),
        stack(
            figure(iv, form="first_6_c"), 
            bass(iv)
        ),
        stack(
            figure(iv, form="second_c", leadin=i),
            bass(vi, v)
        ),
        stack(
            figure(i, form="first_7"), 
            bass(i)
        ),
        stack(
            figure(i, form="second", leadin=iv),
            bass(iii)
        ),
        stack(
            figure(iv, form="first_6"), 
            bass(iv)
        ),
        stack(
            figure(iv, form="second", leadin=i),
            bass(vi, v)
        ),
        stack(
            figure(i, form="first_7"), 
            bass(i),
        ),
        stack(
            figure(i, form="last"), 
            bass(iii, i),
        ),
    )

play(song3(), Config(beats_per_minute=92, note_width=.5))

#play([TUNING], Config(beats_per_minute=10, loops=10))
