from __future__ import annotations # so that Cycles methods can return Cycles instances
from enum import Enum, auto
from midi import Config
from typing import Any

class CycleStringType(Enum):
    NOTES = auto()
    RHYTHM = auto()
    VELOCITY = auto()
    GATE_LENGTH = auto()
    NUDGE = auto()
    STACK = auto()

class Cycles:

    def __init__(self) -> None:
        self.cycle_strings: list[tuple[CycleStringType, str]] = []
        self.midi_file = None
        self.total_secs = None
        self.config = Config()

    def notes(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.NOTES, cycle_string))
        return self

    def rhythm(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.RHYTHM, cycle_string))
        return self

    def velocity(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.VELOCITY, cycle_string))
        return self

    def gate_length(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.GATE_LENGTH, cycle_string))
        return self

    def nudge(self, cycle_string: str) -> Cycles:
        self.cycle_strings.append((CycleStringType.NUDGE, cycle_string))
        return self

    def stack(self) -> Cycles:
        self.cycle_strings.append((CycleStringType.STACK, ""))
        return self

    def set_config(self, param: str, val: Any) -> Cycles:
        setattr(self.config, param, val)
        return self

    def midi(self) -> Cycles:
        # (self.midi_file, self.total_secs) = events_to_midi(voices, self.config, cycle_count)

        return self

    def play(self) -> Cycles:
        # play_midi(self.config, self.total_secs)

        return self

def notes(cycle_string: str) -> Cycles:
    return Cycles().notes(cycle_string)

def rhythm(cycle_string: str) -> Cycles:
    return Cycles().rhythm(cycle_string)

