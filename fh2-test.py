from asciimidi import play, Config

tuning = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""
song1 = """
A4 A4 A4 A4 A4 A4 A4 A4 D5 D5 D5 D5 D5 D5 D5 D5 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4 A4
F2 == == == == == == == B2 == == == == == == == F2 == == == == == == == E2 == == == == == == ==
D2 == == == == == == == G2 == == == == == == == D2 == == == == == == == C2 == == == == == == ==
"""
song2 = """
A4 A4 A4 A4 A4 A4 A4 A4 B4 B4 B4 B4 B4 B4 B4 B4 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5 C5
F2 == == == == == == == G2 == == == == == == == A2 == == == == == == == == == == == == == == ==
D2 == == == == == == == E2 == == == == == == == F2 == == == == == == == == == == == == == == ==
"""
I = """
G3  G3  A3  A3  Bb3 Bb3 A3  A3 
C3  C3  C3  C3  C3  C3  C3  C3 
"""
IV = """
C4  C4  D4  D4  Eb4 Eb4 D4  D4  
F3  F3  F3  F3  F3  F3  F3  F3  
"""
V  =  """
D4  D4  E4  E4  F4  F4  E4  E4  
G3  G3  G3  G3  G3  G3  G3  G3  
"""

config = Config(note_width=.8, swing=.6, loops=10)

twelve_bar = [I, IV, I, I, IV, IV, I, I, V, IV, I, I]
play(twelve_bar, config)
#play([tuning], Config(beats_per_minute=10, loops=10))
