# Set up
```
brew install portmidi # will take a long time to build
python3.7 -m venv my_env
source my_env/bin/activate
pip install --upgrade pip
pip install mido
pip install mido\[ports-rtmidi\]
pip freeze > requirements.txt
pip install -r requirements.txt
deactivate
```

# Run
```
source my_env/bin/activate
python3 fh2-test.py
deactivate
```

# Re-run on save
```
# first time only
brew install entr

# every time
. my_env/bin/activate
echo 2025-08-11.py | entr -r python 2025-08-11.py
deactivate
```

# Test/Typecheck
```
mypy --strict cyclemidi.py
pytest
ruff check cyclemidi.py
ruff format cyclemidi.py
```

# Philsophy
- plain text, no special/proprietary data format
- human readable, especially in a monospaced font
- intuitive: musically inclined readers can guess the basics without reading this
- code-able: composed of strings that can easily be generated/concatenated algorithmically
  - music is all patterns and variations on those patterns...
  - ... so is code
  - expressing music with code gives us a chance to make the patterns and variations clear
    even clearer than they are in conventional sheet music
  - ... and perhaps compose differently because we have the structural aspects at our
    fingertips
 
# To Do
- add mini notation examples here
- 

# Examples
Some music:
```
--- --- --- E4  --- --- --- E4
--- --- G3  --- --- --- G3  ---
--- C3  --- --- --- C3  --- ---
C2  --- --- --- C2  --- --- ---

--- --- --- F4  --- --- --- F4
--- --- B3  --- --- --- B3  ---
--- G3  --- --- --- G3  --- ---
G2  --- --- --- G2  --- --- ---

--- --- E4  --- --- --- --- E4
--- G3  --- --- --- G3  --- ---
--- --- --- C3  --- --- C3  ---
C2  --- --- --- C2  --- --- ---

--- --- F4  --- --- --- --- F4
--- B3  --- --- --- B3  --- ---
--- --- --- G3  --- --- G3  ---
G2  --- --- --- G2  --- --- ---
```

The code that generated it:
```
from asciimidi import play, Config
from note_util import stack, make_lines, Note, set_key, print_ascii, second, third, fourth, fifth, sixth, seventh, oct


def arp_chord(p0, p1, p2, p3):
    return f"""
--- --- --- {p3:3} --- --- --- {p3:3}
--- --- {p2:3} --- --- --- {p2:3} ---
--- {p1:3} --- --- --- {p1:3} --- ---
{p0:3} --- --- --- {p0:3} --- --- ---
"""


def scatter_chord(p0, p1, p2, p3):
    return f"""
--- --- {p3:3} --- --- --- --- {p3:3}
--- {p2:3} --- --- --- {p2:3} --- ---
--- --- --- {p1:3} --- --- {p1:3} ---
{p0:3} --- --- --- {p0:3} --- --- ---
"""


def chord_seq(chord_func):
    C = Note("C3", "C major")
    G = C + fifth

    bars = [
        chord_func(C-oct, C, C+fifth, C+oct+third),
        chord_func(G-oct, G, G+third, G+seventh),
    ]

    return bars


def song():
    scatter_chords = chord_seq(scatter_chord)
    arp_chords = chord_seq(arp_chord)

    bars = arp_chords + scatter_chords

    print_ascii(bars)
    return make_lines(bars)

play(song(), Config(beats_per_minute=122, symbols_per_beat=2, midi_devices=['IAC Driver Bus 1']))
```
