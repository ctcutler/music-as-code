import re
import sys

from mido import MidiFile, MidiTrack, Message, MetaMessage, open_output, Backend, bpm2tempo

ASCII_NOTE_RE = re.compile('(\D+)(\d+)(\+*)(\-*)')
WS_RE = re.compile(' +')
#MIDI_DEVICE = 'Elektron Model:Cycles'
MIDI_DEVICE = 'FH-2'
#MIDI_DEVICE = 'IAC Driver Bus 1'
MIDI_FILE_NAME = 'new_song.mid'

midi_note_numbers = {
  'R': 0, 
  'C': 24, 
  'C#': 25,
  'Db': 25,
  'D': 26, 
  'D#': 27,
  'Eb': 27,
  'E': 28, 
  'F': 29,
  'F#': 30,
  'Gb': 30,
  'G': 31, 
  'G#': 32,
  'Ab': 32,
  'A': 33, 
  'A#': 34,
  'Bb': 34,
  'B': 35, 
}

def get_midi_note(note, octave):
    return midi_note_numbers[note] + (int(octave) * 12)

rest_length = 0
def process_note(track, channel, note, note_start, note_end):
    global rest_length
    if note in ('---', '--'):
        rest_length += note_start + note_end
    else:
        if note in ('===', '=='):
            track[-1].time += note_start + note_end
        else: 
            m = ASCII_NOTE_RE.search(note)
            note, octave, up_volume, down_volume = m.groups()
            midi_note = get_midi_note(note, octave)
            velocity = 60 
            velocity += 20 * len(up_volume) 
            velocity -= 20 * len(down_volume) 

            track.append(
                Message(
                    'note_on',
                    channel=channel,
                    note=midi_note,
                    velocity=velocity,
                    # delta from preceding note_off (or start of song)
                    time=rest_length+note_start
                )
            )
            track.append(
                Message(
                    'note_off',
                    channel=channel,
                    note=midi_note,
                    velocity=velocity,
                    # delta from preceding note_on
                    time=note_end
                )
            )

        rest_length = 0

def ascii_to_midi(asciis, notes_per_beat, note_width, swing, tempo, file_name):
    "Assumes asciis is a list of strings and each has same number of newlines"""
    mid = MidiFile()
    channel = 0
    ticks_per_note = mid.ticks_per_beat // notes_per_beat
    ticks_per_pair = 2 * ticks_per_note
    global rest_length

    # if single str, wrap in list
    if isinstance(asciis, str):
        asciis = [asciis]

    split_by_newline = [a.split('\n') for a in asciis]
    zipped = zip(*split_by_newline)
    music = '\n'.join([' '.join(z) for z in zipped])

    left_swing = swing * ticks_per_pair
    right_swing = (1 - swing) * ticks_per_pair
    left_end = right_end = int(note_width * right_swing)
    left_start = int(right_swing - right_end)
    right_start = int(left_swing - left_end)

    for voice in music.strip().split('\n'):
        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo)))
        notes = WS_RE.split(voice.strip())
        note_pairs = zip(notes[0::2], notes[1::2])

        is_first_pair = True
        for (left, right) in note_pairs:
            process_note(track, channel, left, 0 if is_first_pair else left_start, left_end)
            process_note(track, channel, right, right_start, right_end)
            is_first_pair = False

        mid.tracks.append(track)
        channel += 1
        rest_length = 0

    mid.save(file_name)

    return mid

def play(asciis, notes_per_beat, note_width, swing, tempo, loops=1):
    ascii_to_midi(asciis, notes_per_beat, note_width, swing, tempo, MIDI_FILE_NAME)
    portmidi = Backend('mido.backends.portmidi')
    for i in range(loops):
        with portmidi.open_output(MIDI_DEVICE) as midi_port:
            try:
                for msg in MidiFile(MIDI_FILE_NAME).play():
                    print(msg)
                    midi_port.send(msg)
            except KeyboardInterrupt:
                midi_port.reset()
                sys.exit(1)
