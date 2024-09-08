from note_util import n, set_key

def test(name, expected, actual):
    if expected == actual:
        print(f"{name} PASSED")
    else:
        print(f"{name} FAILED\nexpected: {expected}\nactual: {actual}")

# str of Note
test("str of note", "Ab2", str(n("Ab2", "A minor")))
test("f string of note", "Ab2", f"{n('Ab2')}")

# add in key
set_key("G major")
test("add to note w/key", n("B3"), n("G3", "G major")+2)
test("add to note w/o key", n("A3"), n("G3")+1)
test("add to note cross C octave only", n("D4"), n("B3")+2)
test("add to note cross key octave only", n("A4"), n("D4")+4)
test("add to note cross C & key octave only", n("D4"), n("E3")+6)

# subtract in key
test("subtract from note w/key", n("E3", "E minor"), n("G3", "E minor")-2)
test("subtract from note w/o key", n("F#3"), n("G3")-1)
test("subtract from note cross C octave only", n("B2"), n("D3")-2)
test("subtract from note cross key octave only", n("C4"), n("G4")-4)
test("subtract from note cross C & key octave only", n("A2"), n("G3")-6)

# add in key intervals
set_key("G major")
test("add in key interval to note w/key", n("B3"), n("G3", "G major")+"3rd")
test("add in key interval to note w/o key", n("A3"), n("G3")+"2nd")
test("add in key interval to note cross C octave only", n("D4"), n("B3")+"3rd")
test("add in key interval to note cross key octave only", n("A4"), n("D4")+"5th")
test("add in key interval to note cross C & key octave only", n("D4"), n("E3")+"7th")

# subtract in key intervals
test("subtract in key interval from note w/key", n("E3", "E minor"), n("G3", "E minor")-"3rd")
test("subtract in key interval from note w/o key", n("F#3"), n("G3")-"2nd")
test("subtract in key interval from note cross C octave only", n("B2"), n("D3")-"3rd")
test("subtract in key interval from note cross key octave only", n("C4"), n("G4")-"5th")
test("subtract in key interval from note cross C & key octave only", n("A2"), n("G3")-"7th")

# add fixed intervals
set_key("G major")
test("add fixed interval to note", n("A3"), n("G3")+"M2")
test("add fixed interval to note (leave key)", n("G#3"), n("G3")+"m2")

# subtract fixed intervals
set_key("G major")
test("subtract fixed interval from note", n("F#3"), n("G3")-"m2")
test("subtract fixed interval from note (leave key)", n("F3"), n("G3")-"M2")

