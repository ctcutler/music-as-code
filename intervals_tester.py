from asciimidi import add_semitones, interval, semitone_distance, scale_interval, n, set_key

def test(name, expected, actual):
    if expected == actual:
        print(f"{name} PASSED")
    else:
        print(f"{name} FAILED\nexpected: {expected}\nactual: {actual}")

set_key("C major")

# add_semi_tones
test("add_semi_tones: no octave", n("B3"), add_semitones(n("A3"), 2))
test("add_semi_tones: octave", n("C4"), add_semitones(n("B3"), 1))
test("add_semi_tones: E to F", n("F3"), add_semitones(n("E3"), 1))
test("add_semi_tones: sharps", n("C#4"), add_semitones(n("A#3"), 3))
test("add_semi_tones: flats", n("Db4"), add_semitones(n("Bb3"), 3))
test("add_semi_tones: negative", n("C3"), add_semitones(n("D3"), -2))
test("add_semi_tones: negative octave", n("A2"), add_semitones(n("C3"), -3))

# interval
test("interval: normal", n("F#3"), interval(n("C3"), "TT"))
test("interval: inverted", n("F#2"), interval(n("C3"), "TT", inverted=True))

# semitone_distance
test("semitone_distance: p1 < p2", 3, semitone_distance(n("C3"), n("Eb3")))
test("semitone_distance: p1 > p2", 3, semitone_distance(n("Eb3"), n("C3")))
test("semitone_distance: p1 < p2 (octave up)", 15, semitone_distance(n("C3"), n("Eb4")))
test("semitone_distance: p1 > p2 (octave up)", 15, semitone_distance(n("Eb4"), n("C3")))
test("semitone_distance: p1 < p2 (octave down)", 12-3, semitone_distance(n("C3"), n("Eb2")))
test("semitone_distance: p1 > p2 (octave down)", 12-3, semitone_distance(n("Eb2"), n("C3")))

# scale_interval
test("scale_interval: normal", n("G3", "C major"), scale_interval(n("C3"), 5, "C major"))
test("scale_interval: wrap around degrees", n("F#3", "E minor"), scale_interval(n("C3"), 4, "E minor"))
test("scale_interval: wrap around octaves", n("E3", "C major"), scale_interval(n("A2"), 5, "C major"))
test("scale_interval: wrap around both", n("F#4", "E minor"), scale_interval(n("A3"), 6, "E minor"))

# str of Note
test("str of note", "Ab2", str(n("Ab2", "A minor")))
test("f string of note", "Ab2", f"{n('Ab2')}")

# add in key
note = n("C3", "C major")
test("add to note w/key", n("G3"), note+4)
note = n("G3")
test("add to note w/o key", n("A3"), note+1)
note = n("A3")
test("add to note cross octave", n("E4"), note+4)

# FIXME: test crossing key octave separately from C octave?

# subtract in key

# add steps
# subtract steps

# add arbitrary intervals
# add in key intervals
