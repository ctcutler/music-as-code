from asciimidi import play, Config

tuning = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""


Dm = """
D3 == F3 A3 D4 == A3 F3
D2 == == == == == == ==
"""
G_D = """
D3 == G3 B3 D4 == B3 G3
G2 == == == == == == == 
"""
Em = """
E3 == G3 B3 E4 == B3 G3
E2 == == == == == == ==
"""
Am_E = """
E3 == A3 C4 E4 == C4 A3
A2 == == == == == == ==
"""

config = Config(note_width=.99, swing=.55, loops=10)

song = [ 
  Dm, Dm, G_D, G_D,
  Em, Am_E, Em, Am_E,
  Dm, Dm, G_D, G_D,
  Em, Am_E, Em, Am_E,
]
play(song, config)
#play([tuning], Config(beats_per_minute=10, loops=10))
