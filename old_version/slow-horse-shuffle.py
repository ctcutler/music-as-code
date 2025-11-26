from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

"""
bah-dit-dit BAH
bah-dit-dit BAH
bah-dit-dit BAH
bah-dit-dit dah-dit dah-dit

// X/
// X/
// X/
 x  x

/ /X /
/ /X /
/ /X /
/ // // // /
"""

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

def shuffle_a(b, i, iv, v):
    return f"""
--- --- {v:3} --- --- --- {v:3} ---
{b:3} {b:3} {i:3} {iv:3} {b:3} {b:3} {i:3} {iv:3}
"""

def shuffle_b(b, i, iv, v):
    return f"""
--- --- {v:3} --- --- --- --- ---
{b:3} {b:3} {i:3} {iv:3} {i:3} {iv:3} {i:3} {iv:3}
"""


def song():
    i = Note("A3", "A minor")
    bass_i = i - 14
    iv = i + "4th"
    v = i + "5th"
    pattern = [shuffle_a(bass_i, i, iv, v), shuffle_b(bass_i, i, iv, v)]
    return make_lines(pattern * 10)

play(song(), Config(beats_per_minute=87, swing=.7))

#play([TUNING], Config(beats_per_minute=10, loops=10))
