from asciimidi import play, Config
from note_util import stack, make_lines, Note, set_key, print_ascii, second, third, fourth, fifth, sixth, seventh, oct

"""
Used for 8 Witches
"""
TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

def arp0(p0, p1, p2, p3):
    return f"{p0:3} {p3:3} {p1:3} --- {p2:3} ---"

def arp1(p0):
    p1 = p0 + second
    p2 = p0 + third
    p3 = p0 + fourth
    p4 = p0 + fifth
    return f"{p4:3} {p2:3} {p3:3} {p1:3} {p2:3} {p0:3} {p2:3} {p0:3}"

def arp2(p0):
    p1 = p0 + second
    p2 = p0 + third
    p3 = p0 + fourth
    p4 = p0 + fifth
    return f"{p4:3} {p3:3} {p2:3} {p1:3} {p2:3} --- {p2:3} ---"

def arp3(p0):
    p1 = p0 + second
    p2 = p0 + third
    p3 = p0 + fourth
    p4 = p0 + fifth
    return f"{p4:3} {p3:3} {p2:3} {p1:3} {p0:3} --- {p0:3} ---"

def song():
    i = Note("E2", "E phrygian")
    iii = i + third # C
    iv = i + fourth # D
    v = i + fifth # E

    bars = [
        arp1(i),
        arp3(i),
        arp1(i),
        arp2(i),
        arp1(iv),
        arp3(iv),
        arp1(iv),
        arp2(iv),
    ]

    print_ascii(bars)

    return make_lines(bars*100)

play(song(), Config(beats_per_minute=162, symbols_per_beat=2, midi_devices=['FH-2']))
#play([TUNING], Config(beats_per_minute=10, loops=10, midi_devices=['FH-2']))
