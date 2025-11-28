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
python3 yoursong.py
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
- code-able: composed of strings that can easily be generated/concatenated algorithmically
  - music is all patterns and variations on those patterns...
  - ... so is code
  - expressing music with code gives us a chance to make the patterns and variations clear
    even clearer than they are in conventional sheet music
  - ... and perhaps compose differently because we have the structural aspects at our
    fingertips
- expressive *and* economical: be able to express complex rhythms and harmonies with a 
  minimum of characters
  - this is where the new philosophy diverges from the original
  - we trade off a certain amount of intuitive-ness to get this economy
 
# Syntax

(The following owes a lot to [Tidal Cycles' Mini-Notation](https://tidalcycles.org/docs/reference/mini_notation/) though it is 
*not* fully compatible with that format.)

Western music is written in terms of units (measures) that are all the same length no matter
how many notes they have in them.  We have those units too; we call them "cycles".  In our 
notation, a cycle is indicated by square brackets.  This is a cycle with one note (middle C)
that plays for the entire cycle:

```
[ C4 ]
```

Notice that we don't specify how long the note is (the "4" indicates the octave, not the
duration.   The length of each note in a cycle is inferred from the number of notes or
rests in the cycle.  If there's only one note it lasts the whole cycle.  

By contrast, this cycle has four notes, all the same length:

```
[ D4 D4 D4 D4 ]
```

Each of those D4s is a quarter of the length of the C4 in the first example... we know this
because there are four of them and they divide up their cycle (which is of course the same 
length as the previous one) into quarters.

We write rests with a tilde like this:

```
[ D4 ~ D4 ~ ]
```

The D4s in this example are the same length as the ones in the previous example but there
are only two of them and each one is followed by a rest that takes one quarter of the cycle
time.

In order to express more complex rhythms, you can embed cycles within cycles:

```
[ C3 [ G3 A3 ] C4 D4 ]
```

The embedded cycle, `[ G3 A3 ]` gets a quarter of the outer cycle time's time and divides
it evenly between the G3 and A3 notes within it. If you wrote this in standard musical
notation the measure would have a quarter note C3, followed by two eighth notes (G3, A3)
and then quarter notes C4 and D4.

We support polyphony using commas:

```
[ C3,E3,G3 G3,B3,C4 ]
```

(That's a C major chord for the first half of the cycle followed by a G major for the second
half.)

If you want to substitute a different note each time the cycle plays there is a syntax for
that:

```
[ B2 < D3 D#3 > F#3 ]
```

This cycle plays B2, D3, F#3 on the first repeat and B2, D#3, F#3 on the second.

We can add further rhythmic complexity with "tied" notes:

```
[ A4 C5 - D5 ]
```

In this example A4 plays for a quarter of the cycle then C5 for half the cycle then
D5 for the final quarter.

Tied notes between cycles are also possible:

```
[ A4 E5 ] [ - D5 ]
```

Here the E5 plays for the length of one cycle, the first half of it in the first 
cycle and the rest in the second cycle.
 
# API

The API provides a fluent (method chaining) interface that starts with a call to
`notes()` which accepts a string containing one or more cycles.  `stack()` allows
multiple cycles to play simultaneously.  `set_config()` enables control of various
configuration options.  `midi()` generates MIDI messages and `play()` sends them
to the specified MIDI interface.  

Here's an example:

```
from midi import  Config
from cyclemidi import notes


notes(
    """
    [ C5,E5,B5 D5,F#5,B5 ]
    [ E5,G5,B5 D5,F#5,B5 ]
    [ C5,E5,B5 D5,F#5,B5 ]
    [ D5,G5,B5 ]
    """
).stack(
).notes(
    """
    [ C2 B1 ]
    [ E2 D2 ]
    [ C2 F#2 ]
    [ G2 ]
    """
).set_config(
    "midi_devices", ['IAC Driver Bus 1']
).set_config(
    "note_width", 0.8
).set_config(
    "beats_per_measure", 8
).set_config(
    "beats_per_minute", 120
).midi().play()
```
