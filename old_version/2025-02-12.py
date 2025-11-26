from asciimidi import play, Config
from note_util import stack, make_lines, Note, set_key, print_ascii, second, third, fourth, fifth, sixth, seventh, oct

"""
Used for Feel Free
"""
TUNING = """
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
C4 == == == == == == ==
"""

MORSE_CODE = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",

# disallowing numbers (for now) so that
# everything will fit in 16 (14, actually) time units
#
#    "1": ".----",
#    "2": "..---",
#    "3": "...--",
#    "4": "....-",
#    "5": ".....",
#    "6": "-....",
#    "7": "--...",
#    "8": "---..",
#    "9": "----.",
#    "0": "-----",

}

MAX_UNITS = 14

def chord(letters, notes):
    chord_lines = []
    for i in range(len(letters)):
        chord_line = ""
        for ditdah in MORSE_CODE[letters[i]]:
            assert(ditdah == '-' or ditdah == '.')

            if ditdah == "-":
               chord_line += f"{notes[i]:3} === === --- "
            else:
               chord_line += f"{notes[i]:3} --- "

        chord_lines.append(chord_line)

    chord_lines = [ 
        chord_line + ((((MAX_UNITS*4) - len(chord_line))//4) * "--- ")
        for chord_line in chord_lines 
    ]

    return "\n".join(chord_lines)

def song():
    i = Note("G2", "G minor")
    iii = i + third # B
    iv = i + fourth # C
    v = i + fifth # D

    Gm0 = [i, i+fifth, i+oct+third, i+oct+oct]
    Gm1 = [i, i+oct, i+oct+fifth, i+oct+oct+third]
    Bb0 = [iii, iii+oct, iii+oct+third, iii+oct+oct+fifth]
    Bb1 = [iii, iii+fifth, iii+oct+oct, iii+oct+oct+oct]
    Cm0 = [iv-fourth, iv+third, iv+oct, iv+oct+oct]
    Cm1 = [iv-sixth, iv, iv+oct+fifth, iv+oct+oct+fifth]
    Dm0 = [v-fourth, v+fifth, v+oct+third, v+oct+oct]
    Dm1 = [v-sixth, v+third, v+oct, v+oct+fifth]

    bars = [
        chord(list("feel"), Gm0),
        chord(list("free"), Bb0),
        chord(list("stay"), Dm0),
        chord(list("open"), Cm0),
        chord(list("keep"), Gm1),
        chord(list("safe"), Dm1),
        chord(list("stay"), Cm1),
        chord(list("gold"), Bb1),
    ]

    print_ascii(bars)

    return make_lines(bars*8)

# each measure is 14 symbols long, if each symbol is a 16th note then the signature is 7/8
play(song(), Config(beats_per_minute=180, symbols_per_beat=2, midi_devices=['FH-2']))
#play([TUNING], Config(beats_per_minute=10, loops=10, midi_devices=['FH-2']))
