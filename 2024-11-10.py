from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

"""
X-X--XX-

Cmaj7: C G B E
Am7: E A C G
F7: F A C E
G: D G B D
"""
TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

def chord_bar_a(chord):
    # {chord[0]:3} === {chord[0]:3} === === {chord[0]:3} {chord[0]:3} ===
    return f"""
{chord[3]:3} === === === === === === ===
{chord[2]:3} === === === === === === ===
{chord[1]:3} === === === === === === ===
{chord[0]:3} === === === === === === ===
"""

def chord_bar_b(chord):
    # {chord[1]:3} === {chord[1]:3} === === {chord[1]:3} {chord[1]:3} ===
    return f"""
{chord[3]:3} === === === === === === ===
{chord[2]:3} === === === === === === ===
{chord[1]:3} === === === === === === ===
{chord[0]:3} === === === === === === ===
"""

def song():
    i = Note("C2", "C major")
    iv = i + "4th"
    v = i + "5th"
    vi = i + "6th"
    #Cmaj7 = (i, i+"5th", i+"7th", i+"oct"+"3rd")
    Cmaj7 = (i, i+"5th", i+"oct", i+"oct"+"3rd")
    Am7 = (vi-"4th", vi, vi+"3rd", vi+"7th")
    F7 = (iv, iv+"3rd", iv+"5th", iv+"7th")
    G = (v-"4th", v, v+"3rd", v+"5th")
    bars = [
        chord_bar_a(Cmaj7),
        chord_bar_b(Am7),
        chord_bar_a(F7),
        chord_bar_b(G),
    ]
    return make_lines(bars*100)

play(song(), Config(beats_per_minute=67))

#play([TUNING], Config(beats_per_minute=10, loops=10))
