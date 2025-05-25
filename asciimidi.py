import re

from mido import MidiFile, bpm2tempo, tick2second, MidiTrack, Message, MetaMessage

from midi import get_midi_note_and_velocity, play_midi

WS_RE = re.compile(' +')

rest_length = 0
def process_symbol(track, channel, symbol, symbol_start, symbol_end):
    global rest_length
    if symbol in ('---', '--'):
        rest_length += symbol_start + symbol_end
    else:
        if symbol in ('===', '=='):
            track[-1].time += symbol_start + symbol_end
        else: 
            midi_note, velocity = get_midi_note_and_velocity(symbol)

            track.append(
                Message(
                    'note_on',
                    channel=channel,
                    note=midi_note,
                    velocity=velocity,
                    # delta from preceding note_off (or start of song)
                    time=rest_length+symbol_start
                )
            )
            track.append(
                Message(
                    'note_off',
                    channel=channel,
                    note=midi_note,
                    velocity=velocity,
                    # delta from preceding note_on
                    time=symbol_end
                )
            )

        rest_length = 0


def ascii_to_midi(asciis, config):
    "Assumes asciis is a list of strings and each has same number of newlines"""
    mid = MidiFile()
    channel = 0
    ticks_per_symbol = mid.ticks_per_beat // config.symbols_per_beat
    ticks_per_pair = 2 * ticks_per_symbol
    tempo = bpm2tempo(config.beats_per_minute)
    global rest_length

    # if single str, wrap in list
    if isinstance(asciis, str):
        asciis = [asciis]

    split_by_newline = [a.split('\n') for a in asciis]
    zipped = zip(*split_by_newline)
    music = '\n'.join([' '.join(z) for z in zipped])

    left_swing = config.swing * ticks_per_pair
    right_swing = (1 - config.swing) * ticks_per_pair
    left_end = right_end = int(config.note_width * right_swing)
    left_start = int(right_swing - right_end)
    right_start = int(left_swing - left_end)

    # reversed() so that the "bottom" voice is channel 0
    max_symbol_count = 0
    for voice in reversed(music.strip().split('\n')):
        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=tempo))
        symbols = WS_RE.split(voice.strip())
        symbol_pairs = list(zip(symbols[0::2], symbols[1::2]))
        max_symbol_count = max(max_symbol_count, len(symbol_pairs) * 2)

        is_first_pair = True
        for (left, right) in symbol_pairs:
            process_symbol(track, channel, left, 0 if is_first_pair else left_start, left_end)
            process_symbol(track, channel, right, right_start, right_end)
            is_first_pair = False

        mid.tracks.append(track)
        channel += 1
        rest_length = 0

    mid.save(config.midi_file_name)

    return (mid, tick2second(max_symbol_count * ticks_per_symbol, mid.ticks_per_beat, tempo))

def play_ascii(asciis, config):
    (ignore, total_secs) = ascii_to_midi(asciis, config)
    play_midi(config, total_secs)


