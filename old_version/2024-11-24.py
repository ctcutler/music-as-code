from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

"""
--- --- A2  ===    --- --- B2  ===
--- --- --- ---    --- --- --- ---
C2  === C2  ===    E2  === E2  ===
--- --- --- ---    C2  === C2  ===

01001100

0: rest
1: note

-vs-

0: note a
1: note b

the latter, obvs, being more of a harmonic thing and less of a rhythmic thing
though there is still rhythm there
"""

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def interval_by_letter(p0, p1, p2, p3, l):
    """
    Ooh, this is messy.  So we want to fill in three voices @ 8 eighth notes each 
    and we have 8 bits to do it with. And we can make, I dunno, a bunch of notes
    off of the bass note.  We could just use bits to decide octave of the notes
    in the chord. So voice n is in octave n when it gets a 0 and octave n+1 when it 
    gets a 1. 

    OK, so maybe the three voices is what's making this hard and I should go back to 
    four.  

    I mean, one thing to do would be to have different voices do different things
    with a 1 or a zero and then feed them all the same pattern

    v3: 
    v2: 8th on 0s, 7th on 1s
    v1: 3rd on 0s, 5th on 1s
    v0: always root, just new gate on every time the value is different from the
    previous.

    Fuck.  Or I could just have some nice chords.  


    v0 = ""
    v1 = ""
    v2 = ""
    v3 = ""
    for i in range(7, -1, -1):
        if i > 5:
        if i > 3:
        if i > 1:
        else:

            v3 += f"{p3:3} === " if ord(l) >> i & 1 else "--- --- "
        elif i > 1:
            v2 += f"{p2:3} === " if ord(l) >> i & 1 else "--- --- "
        else:
            v1 += f"{p1:3} === === === " if ord(l) >> i & 1 else "--- --- --- --- "

    # root is always on
    v0 += f"{p0:3} === === === === === === === "

    return stack(v3, v2, v1, v0)
    """
    pass

def interval(p0, p1, p2, p3):
    return f"""
{p3:3} === === === === === === --- ---
{p2:3} === === === === === === --- ---
{p1:3} === === === === === === --- ---
{p0:3} === === === === === === --- ---
"""

def song():
    i = Note("A1", "A minor")
    ii = i + "2nd"
    mii = i + "m2"
    iii = i + "3rd"
    iv = i + "4th"
    v = i + "5th"
    vi = i + "6th"
    vii = i + "7th"

    # Am
    # C
    # G
    # Bb
    bars = [
        interval(i, iii, v, i+"8th"),
        interval(iii, v, vii, iii+"8th"),
        interval(vii-"8th", ii, iv, vii),
        interval(mii, iv, vi, mii+"P8"),
    ]
    return make_lines(bars*100)

play(song(), Config(beats_per_minute=105))

#play([TUNING], Config(beats_per_minute=10, loops=10))


