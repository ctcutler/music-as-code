from note_util import n, set_key

def test_str_of_note():
    # str of note
    assert "Ab2" == str(n("Ab2", "A minor"))
    # f string of note
    assert "Ab2" == f"{n('Ab2')}"
    # f string of note with special formatting
    assert "Ab2" == f"{n('Ab2'):3}"

def test_add_in_key():
    set_key("G major")
    # add to note w/key
    assert n("B3") == n("G3", "G major")+2
    # add to note w/o key
    assert n("A3") == n("G3")+1
    # add to note cross C octave only
    assert n("D4") == n("B3")+2
    # add to note cross key octave only
    assert n("A4") == n("D4")+4
    # add to note cross C & key octave only
    assert n("D4") == n("E3")+6

def test_subtract_in_key():
    # subtract from note w/key
    assert n("E3", "E minor") == n("G3", "E minor")-2
    # subtract from note w/o key
    assert n("F#3") == n("G3")-1
    # subtract from note cross C octave only
    assert n("B2") == n("D3")-2
    # subtract from note cross key octave only
    assert n("C4") == n("G4")-4
    # "subtract from note cross C & key octave only
    assert n("A2") == n("G3")-6

def test_add_in_key_intervals():
    set_key("G major")
    # add in key interval to note w/key
    assert n("B3") == n("G3", "G major")+"3rd"
    # add in key interval to note w/o key
    assert n("A3") == n("G3")+"2nd"
    # add in key interval to note cross C octave only
    assert n("D4") == n("B3")+"3rd"
    # add in key interval to note cross key octave only
    assert n("A4") == n("D4")+"5th"
    # add in key interval to note cross C & key octave only
    assert n("D4") == n("E3")+"7th"

def test_subtract_in_key_intervals():
    # subtract in key interval from note w/key
    assert n("E3", "E minor") == n("G3", "E minor")-"3rd"
    # subtract in key interval from note w/o key
    assert n("F#3") == n("G3")-"2nd"
    # subtract in key interval from note cross C octave only
    assert n("B2") == n("D3")-"3rd"
    # subtract in key interval from note cross key octave only
    assert n("C4") == n("G4")-"5th"
    # subtract in key interval from note cross C & key octave only
    assert n("A2") == n("G3")-"7th"

def test_add_fixed_intervals():
    set_key("G major")
    # add fixed interval to note
    assert n("A3") == n("G3")+"M2"
    # add fixed interval to note (leave key)
    assert n("G#3") == n("G3")+"m2"

def test_subtract_fixed_intervals():
    set_key("G major")
    # subtract fixed interval from note
    assert n("F#3") == n("G3")-"m2"
    # subtract fixed interval from note (leave key)
    assert n("F3") == n("G3")-"M2"
