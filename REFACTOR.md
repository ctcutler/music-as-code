# Motivation

As I have added and refined features, the internal architecture of this tool has grown without an overarching design or structure.  I want to add a new feature (tied notes between cycles) that will just make this mess worse.  Before I do that I'm considering refactoring the whole thing to make it easier to implement this new feature and many more to come.  

# TODO

- [ ] design
- [ ] refactor/port tests to an actual testing framework
- [ ] implement

# Major Functionality

(Listed here as an aid to "testing" my design.)

- cycles and nested cycles
- alternative syntax: "< >"
- polyphony within a single cycle: ","
- polyphony via "stacked" cycles
- a note width parameter that effects how long the note is actually "on" during the time allotted to it
- rests
- the ability to define various quantities of swing
- the ability to "merge" cycles that define different note parameters, e.g.:
  - pitch
  - rhythm
  - velocity

# Architectural Overview

- The API collects inputs (strings containing cycle syntax, other parameters).
- Parsing iterates over the input strings and builds an instance of the data model.
- [let's leave open the possibility that for clarity we make a pass over the data model to convert from objects that are easily parsed *into* to objects that are easily generated *from*.]
- MIDI generation traverses the data model and generates a MIDI messages.
- MIDI messages are output in sequence and with (reasonably) accurate timing.

Note that although the API collects inputs in a series of method calls, there's no expectation that any parsing or generation occurs until the caller signals they have no more input to provide.  (I'm assuming that not leaving the door open for more input and instead being able to rely on having all of it will make the design simpler and easier.

And note that I'm setting a goal of avoiding a tight coupling between the data model's concepts and MIDI's concepts.  Which is to say, the data model should support simple and clear MIDI message generation but the data model should know about channels or "note on" vs. "note off" or anything like that.

# Data Model

- note: has start time, end time, width, offset, pitch, and zero or more modulations
  - velocity is the only pre-defined modulation but we'll support others that the user defines
  - start time and end time define the duration allotted to the note within the sequence
    - time values are improper Fractions that indicate both the measure (the whole number) and the location within that measure (the fraction)
  - width defines how long the note is actually "on" within its allotted space
  - offset defines when the note starts within its allotted space (this will be helpful for swung notes)

- rest: special case of note that represents silence and therefore has start and end but no pitch or modulations
  - Q: will explicit rests be necessary/convenient or can we just assume that all gaps between notes in a given voice are rests?

- voice: a sequence of notes, strictly monophonic 

- voices: the N voices needed to represent the polyphony required by the caller

Not part of the data model but for reference, mido MIDI messages contain:
- type (note_on/note_off)
- time
- note number (pitch)
- velocity
- channel

# Details

## Parsing
- the API provides a list of cycle strings and a config object
- every cycle string has a type (NOTES, RHYTHM, VELOCITY, STACK, etc.)
- for each cycle string:
  - parse the string and add notes to the relevant voice(s)
  - relevant voices are determined by:
    - the amount of polyphony in the cycle string
    - how many STACKs we've already seen
  - [TODO: lots of complexity here in support of nested cycles, alternatives, polyphony, ties, merges]


## MIDI Generation
- for every voice:
  - for every note in the voice:
    - generate note_on and note_off messages in this voice's channel, taking start time, end time, width, offset, pitch, velocity into account
- sort the note_on and not_off messages by time before playing them

