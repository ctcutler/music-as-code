from asciimidi import add_semitones, scale_note, interval, semitone_distance, scale_interval

def test(name, expected, actual):
    if expected == actual:
        print(f"{name} PASSED")
    else:
        print(f"{name} FAILED\nexpected: {expected}\nactual: {actual}")

# add_semi_tones
test("add_semi_tones: no wrap", "B3", add_semitones("A3", 2))
test("add_semi_tones: wrap", "A4", add_semitones("G3", 2))
test("add_semi_tones: E to F", "F3", add_semitones("E3", 1))
test("add_semi_tones: sharps", "C#3", add_semitones("A#3", 3))
test("add_semi_tones: flats", "Db3", add_semitones("Bb3", 3))
test("add_semi_tones: negative", "A3", add_semitones("C3", -3))
test("add_semi_tones: negative wrap", "G#2", add_semitones("A3", -1))

# scale_note
test("scale_note: major", "E3", scale_note("C", "major", "III", 3))
test("scale_note: minor", "G#2", scale_note("F", "minor", "III", 2))
test("scale_note: flat", "D4", scale_note("Eb", "major", "VII", 4))

# interval
test("interval: normal", "F#3", interval("C3", "TT"))
test("interval: inverted", "F#2", interval("C3", "TT", inverted=True))

# semitone_distance
test("semitone_distance: p1 < p2", 3, semitone_distance("C", "Eb"))
test("semitone_distance: p1 > p2", 6, semitone_distance("F#", "C"))

# scale_interval
test("scale_interval: normal", "G3", scale_interval("C", "major", "C3", 5))
test("scale_interval: wrap around degrees", "F#3", scale_interval("E", "minor", "C3", 4))
test("scale_interval: wrap around octaves", "E3", scale_interval("C", "major", "A2", 5))
test("scale_interval: wrap around both", "F#4", scale_interval("E", "minor", "A3", 6))
