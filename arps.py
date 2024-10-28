from asciimidi import play, Config
from note_util import stack, concat, make_lines, Note, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""


#def quarter_eighth_4_arp(chord):
#    n0, n1, n2, n3 = chord
#    return f"""
#{n0:3} === === === {n1:3} === {n2:3} === === === {n3:3} ===
#"""
#
#def dotted_eighth_4_arp(chord):
#    n0, n1, n2, n3 = chord
#    return f"""
#{n0:3} === === {n1:3} === === {n2:3} === === {n3:3} === ===
#"""
#def sixteenth_4_arp(chord):
#    n0, n1, n2, n3 = chord
#    return f"""
#{n0:3} {n1:3} {n2:3} {n3:3} {n0:3} {n1:3} {n2:3} {n3:3} {n0:3} {n1:3} {n2:3} {n3:3}
#"""


def sixteenth_3_arp(chord):
    n0, n1, n2, n3 = chord
    return f"""
{n0:3} {n1:3} {n2:3} {n0:3} {n1:3} {n2:3} {n0:3} {n1:3} {n2:3} {n0:3} {n1:3} {n2:3}
"""

def eighth_3_arp(chord):
    n0, n1, n2, n3 = chord
    return f"""
{n0:3} === {n1:3} === {n2:3} === {n0:3} === {n1:3} === {n2:3} ===
"""

def quarter_3_arp(chord):
    n0, n1, n2, n3 = chord
    return f"""
{n0:3} === === === {n1:3} === === === {n2:3} === === ===
"""

def quarter_3_arp_alt(chord):
    n0, n1, n2, n3 = chord
    # FIXME: if I wanna use this, looks like a case for doing in key + 
    # semitone arithmetic...
    return quarter_3_arp([n0+"3rd", n1+"7th", n2+"3rd", n3+"5th"])

def rest(chord):
    return f"""
--- --- --- --- --- --- --- --- --- --- --- ---
"""

def shift_octave(note, shift):
    shifted = note
    while shift != 0:
        if shift > 0:
            shifted += 'P8'
            shift -= 1
        else:
            shifted -= 'P8'
            shift += 1
    return shifted
    
def make_arp(fn, shift):
    "FIXME: better name for this?"

    def f(chord):
        return fn([shift_octave(note, shift) for note in chord])

    return f

def song():
    i = Note("C3", "C major")
    iii = i + "3rd"
    v = i + "5th"
    vi = i + "6th"
    vii = i + "7th" 

    C = [i, iii, v, i+"oct"]
    Am = [vi-"oct", i, iii, vi]
    Em = [iii, v, vii, iii+"oct"]
    C7 = [i, iii, i+"m7", v]

    chords = [ C, Am, Em, C7 ]

    repeats = [
        [
            make_arp(sixteenth_3_arp, -1),
            make_arp(rest, 0),
            make_arp(rest, 0),
            make_arp(rest, 0),
        ],
        [
            make_arp(sixteenth_3_arp, -1),
            make_arp(quarter_3_arp, -2),
            make_arp(rest, 0),
            make_arp(rest, 0),
        ],
        [
            make_arp(sixteenth_3_arp, -1),
            make_arp(quarter_3_arp, -2),
            make_arp(quarter_3_arp, 0),
            make_arp(rest, 0),
        ],
        [
            make_arp(sixteenth_3_arp, -1),
            make_arp(quarter_3_arp, -2),
            make_arp(quarter_3_arp, 0),
            make_arp(eighth_3_arp, 2),
        ],
        [
            make_arp(rest, 0),
            make_arp(quarter_3_arp, -2),
            make_arp(quarter_3_arp, 0),
            make_arp(eighth_3_arp, 2),
        ],
        [
            make_arp(rest, 0),
            make_arp(rest, 0),
            make_arp(quarter_3_arp, 0),
            make_arp(eighth_3_arp, 2),
        ],
        [
            make_arp(rest, 0),
            make_arp(rest, 0),
            make_arp(rest, 0),
            make_arp(eighth_3_arp, 2),
        ],
    ]

    measures = []
    for repeat in repeats:
        for chord in chords:
            measures.append(
                stack(
                    [arp(chord) for arp in repeat]
                )
            )

    return make_lines(measures)

play(song(), Config(beats_per_minute=92, note_width=.5, symbols_per_beat=2))

#play([TUNING], Config(beats_per_minute=10, loops=10))
