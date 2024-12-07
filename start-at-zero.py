from asciimidi import play, Config
from note_util import stack, concat, make_lines, n, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

def song():
    """
    ACE x 4 Am
    ADF x 4 Dm
    GBE x 4 Em
    FGB x 4 G7

    """
    set_key("A minor")
    Am = (n("A3"), n("C4"), n("E4"))
    Dm = (n("A3"), n("D4"), n("F4"))
    Em = (n("G3"), n("B3"), n("E4"))
    C = (n("G3"), n("C4"), n("E4"))
    chords = [Am, Dm, Em, C]
    bars = []

    for (i, chord) in enumerate(chords):
        root = chord[0] - 14
        third = chord[1] - 14
        fifth = chord[2] - 14
        patterns = [
            f"{chord[0]:3} {chord[1]:3} {chord[2]:3} {chord[0]:3} {chord[2]:3} {chord[1]:3}",
            f"{chord[0]:3} {chord[0]:3} {chord[0]:3} {chord[2]:3} {chord[1]:3} {chord[0]:3}",
            f"{chord[0]:3} --- --- {chord[1]:3} ---  ---",
            f"--- {chord[0]:3} --- {chord[1]:3} --- {chord[2]:3}",
        ]
        bars.append(
            stack([
                f"{fifth:3} === === === {fifth:3} ===",
                f"{third:3} === === === {third:3} ===",
                f"{root:3} === === === {root:3} ===",
                patterns[i]
            ])
        )

    return make_lines(bars*8)

play(song(), Config(beats_per_minute=62, symbols_per_beat=3, note_width=.25))

#play([TUNING], Config(beats_per_minute=10, loops=10))
