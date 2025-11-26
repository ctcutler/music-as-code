from asciimidi import play, Config
from note_util import stack, make_lines, Note, set_key, print_ascii, second, third, fourth, fifth, sixth, seventh, oct

"""
Used for "Off" (https://write.fawm.org/songs/309609)
"""



TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

# mutes contstants
DRUMS = "drums"
BASS = "bass"
BARITONE = "baritone"

def baritone(p0, p1):
    return f"""
{p0:3} --- {p0:3} --- {p0:3} --- {p0:3} --- {p1:3} --- {p1:3} --- {p1:3} --- {p1:3} --- 
"""

def bass0(p0):
    return f"""
{p0:3} --- --- --- {p0:3} --- --- --- --- --- --- --- --- --- --- ---
"""

def bass1(p0):
    return f"""
{p0:3} --- --- --- {p0:3} --- --- --- {p0:3} --- --- --- --- --- --- ---
"""


def bass2(p0, p1):
    return f"""
{p0:3} --- --- {p1:3} {p0:3} --- --- {p1:3} {p0:3} --- --- --- {p0:3} --- --- ---
"""

def bass3(p0):
    return f"""
--- --- --- --- --- --- --- --- {p0:3} --- --- --- --- --- --- --- 
"""


def rest():
    return f"""
--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 
"""

def hat():
    return f"""
C2  --- --- --- C2  --- --- --- C2  --- --- --- C2  --- --- ---
"""

def snare():
    return f"""
--- --- --- --- --- --- --- --- C3  --- --- --- --- --- --- ---
"""

def kick0():
    return f"""
C3  --- --- --- --- --- --- --- --- --- --- --- --- --- --- C3
"""

def kick1():
    return f"""
C3  --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
"""

def measure(baritone, bass, kick, mutes):
    return stack(
        hat() if DRUMS not in mutes else rest(),
        snare() if DRUMS not in mutes else rest(),
        kick if DRUMS not in mutes else rest(),
        rest(),
        rest(),
        baritone if BARITONE not in mutes else rest(),
        bass if BASS not in mutes else rest(),
    )

def section(p0, leading, mutes=[]):
    return [
        measure(
            baritone(p0, p0),
            bass0(p0),
            kick0(),
            mutes,
        ),
        measure(
            baritone(p0+fifth, p0+fourth),
            bass1(p0),
            kick1(),
            mutes,
        ),

        measure(
            baritone(p0, p0),
            bass2(p0, p0-third),
            kick0(),
            mutes,
        ),
        measure(
            baritone(p0+fourth, p0+third),
            bass3(p0),
            kick1(),
            mutes,
        ),
        measure(
            baritone(p0, p0),
            bass2(p0, p0-third),
            kick0(),
            mutes,
        ),
        measure(
            baritone(p0+fifth, leading),
            bass3(p0),
            kick1(),
            mutes,
        ),
    ]

def end(p0):
    return [
        stack(
            rest(),
            rest(),
            rest(),
            rest(),
            rest(),
            rest(),
            bass0(p0),
        )
    ]


def song():
    i = Note("G2", "G minor")

    bars = section(i, i+fourth, mutes=[DRUMS, BASS]) +\
        section(i+fifth, i+second, mutes=[DRUMS, BASS]) +\
        section(i, i+fourth, mutes=[DRUMS]) +\
        section(i+fifth, i+second, mutes=[DRUMS]) +\
        section(i, i+fourth) +\
        section(i+fifth, i+second) +\
        section(i, i+fourth, mutes=[BARITONE, DRUMS]) +\
        end(i)

    print_ascii(bars)

    return make_lines(bars)

play(song(), Config(beats_per_minute=108, symbols_per_beat=4, midi_devices=['Elektron Model:Cycles', 'FH-2']))
#play([TUNING], Config(beats_per_minute=10, loops=10))
