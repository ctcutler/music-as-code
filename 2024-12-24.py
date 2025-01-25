from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

"""
A -> F                            A -> E
F2  === === === === === --- ---   E2  === === === === === --- ---
D2  === === === === === --- ---   C#2 === === === === === --- ---
A1  === === === === === --- ---   A1  === === === === === --- ---

A -> F                            A -> E
F2  === === === === === --- ---   E2  === === === === === --- ---
D2  === === === === === --- ---   C#2 === === === === === --- ---
A1  === === === === === --- ---   A1  === === === === === --- ---

D -> G                            F -> D
D2  === === === === === --- ---   F2  === === === === === --- ---
Bb1 === === === === === --- ---   D2  === === === === === --- ---
G1  === === === === === --- ---   A1  === === === === === --- ---

A -> C                            A -> C#
E2  === === === === === --- ---   E2  === === === === === --- ---
C2  === === === === === --- ---   C#2 === === === === === --- ---
A1  === === === === === --- ---   A1  === === === === === --- ---


swirling, mstepping, twisting voices, a choir with an edge

- modulate mix between the three voices so that only one or two are in prominence at any moment
- modulate stereo panning
- modulate timbre at the filter and at the oscillator (?)
- very easy gradual on and off envelopes 
- slew the pitch changes, maybe even have the pitch go a little bit off before coming back to true

- three square waves
  - left, right
  - always on though they do have slow p -> f envelopes
  - modulation on LPF cutoff
  - modulation on amplitude 
  - modulation on stereo position
  - slewed pitch changes


modifications:
- triangle waves and wave folders not square waves
- proper (if slow) envelopes
- tremelo or vibrato
"""

TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""


def pattern(p0, p1, p2):
    return f"""
{p2:3} === === === === === --- ---
{p1:3} === === === === === --- ---
{p0:3} === === === === === --- ---
"""

def song():
    """
    Dm, A, Dm, A, Gm, Am, A
    """
    i = Note("D3", "D minor")

    Dm = (i-"4th", i+"8th", i+"8th"+"3rd")
    A = (i-"4th", i-"m2", i+"2nd")
    Gm = (i-"5th", i-"3rd", i)
    Am = (i-"4th", i-"2nd", i+"2nd")

    bars = [ 
        pattern(*Dm), pattern(*A), 
        pattern(*Dm), pattern(*A), 
        pattern(*Gm), pattern(*Dm),
        pattern(*Am), pattern(*A),
    ]
    return make_lines(bars*100)

#play(song(), Config(beats_per_minute=78))

play([TUNING], Config(beats_per_minute=10, loops=10))


