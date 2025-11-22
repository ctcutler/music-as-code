from __future__ import annotations  # so that Cycles methods can return Cycles instances
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from enum import Enum, auto
from midi import Config
from typing import Any, Union



class CycleStringType(Enum):
    NOTES = auto()
    RHYTHM = auto()
    VELOCITY = auto()
    GATE_LENGTH = auto()
    NUDGE = auto()
    STACK = auto()

@dataclass
class Rest:
    start:Fraction
    end:Fraction

@dataclass
class Note:
    start:Fraction
    end:Fraction
    pitch:str
    velocity:int
    width:Decimal
    offset:Decimal

Voice = list[Union[Note, Rest]]
CycleString = tuple[CycleStringType, str]

class Cycles:
    def __init__(self) -> None:
        self.cycle_strings: list[CycleString] = []
        self.midi_file = None
        self.total_secs = None
        self.config = Config()


    # "private" methods
    def _parse_cycle_strings(self, cycle_strings: list[CycleString]) -> list[Voice]:
        voices: list[Voice] = [[]]
        base_voice_idx = 0
        for (cycle_string_type, cycle_string) in cycle_strings:
            if cycle_string_type == CycleStringType.STACK:
                voices.append([])
                base_voice_idx = len(voices) - 1
            elif cycle_string_type == CycleStringType.NOTES:
                pass

        return voices

    def _generate_midi(self, voices: list[Voice]) -> None:
        pass

    # "public" methods
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
        voices = self._parse_cycle_strings(self.cycle_strings)
        self._generate_midi(voices)

        return self

    def play(self) -> Cycles:
        # play_midi(self.config, self.total_secs)

        return self


def notes(cycle_string: str) -> Cycles:
    return Cycles().notes(cycle_string)


def rhythm(cycle_string: str) -> Cycles:
    return Cycles().rhythm(cycle_string)
