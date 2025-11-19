from midi import Config

# cycle string types
NOTES = "NOTES"
RHYTHM = "RHYTHM"
VELOCITY = "VELOCITY"
GATE_LENGTH = "GATE_LENGTH"
NUDGE = "NUDGE"
STACK = "STACK"

def notes(cycle_string):
    return Cycles().notes(cycle_string)

def rhythm(cycle_string):
    return Cycles().rhythm(cycle_string)

class Cycles:

    def __init__(self):
        self.cycle_strings = []
        self.midi_file = None
        self.total_secs = None
        self.config = Config()

    def notes(self, cycle_string):
        self.cycle_strings.append((NOTES, cycle_string))
        return self

    def rhythm(self, cycle_string):
        self.cycle_strings.append((RHYTHM, cycle_string))
        return self

    def velocity(self, cycle_string):
        self.cycle_strings.append((VELOCITY, cycle_string))
        return self

    def gate_length(self, cycle_string):
        self.cycle_strings.append((GATE_LENGTH, cycle_string))
        return self

    def nudge(self, cycle_string):
        self.cycle_strings.append((NUDGE, cycle_string))
        return self

    def stack(self):
        self.cycle_strings.append((STACK, ""))
        return self

    def set_config(self, param, val):
        setattr(self.config, param, val)
        return self

    def midi(self):
        # (self.midi_file, self.total_secs) = events_to_midi(voices, self.config, cycle_count)

        return self

    def play(self):
        # play_midi(self.config, self.total_secs)

        return self
