'''
Reads midi file and then maps track info to haptic glove
'''

import mido
from mido import Message, MidiFile, MidiTrack
import os
import math
import argparse
from BreakfastSerial import Arduino, Led
import time


parser = argparse.ArgumentParser(description='Play midi with the haptic feedback glove!')
parser.add_argument('midi_file', help='enter the midi file name')
args = parser.parse_args()


# print(mido.get_input_names())
# print(mido.get_output_names())

# inport = mido.open_input('MPKmini2')
# outport = mido.open_outport()
TEMPO = mido.bpm2tempo(100) # expresses bpm in microseconds per beat for mido
# print("default tempo = {}\n".format(TEMPO))
board = Arduino()
print("COnnectedt")
#
# # notemap = {'e':3, 'd':4, 'c':5, 'b':6}
notemap = {'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6}
ledmap = {k:Led(board, v) for (k,v) in notemap.items()}


def get_midi_tempo(midiFile):
    for i, track in enumerate(midiFile.tracks):
        print('Track {}:'.format(i))
        for msg in track:
            print('  {!r}'.format(msg))
            if msg.is_meta:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
            elif not msg.is_meta:
                # print('  {!r}'.format(msg))
                pass
        print('\n')
    return tempo


def midifile_to_dict(mid):
    tracks = []
    for track in mid.tracks:
        tracks.append([vars(msg).copy() for msg in track])

    midi_dict = dict({'ticks_per_beat': mid.ticks_per_beat,
                      'tracks': tracks
                      })
    return midi_dict


def get_track_features(midiFile):

    feat_dict = dict()
    track = midiFile.tracks[0]
    for msg in track:

        if msg.is_meta:
            if msg.type == 'track_name':
                feat_dict[msg.type] = msg.name
            elif msg.type == 'time_signature':
                feat_dict[msg.type] = [msg.numerator, msg.denominator]
            elif msg.type == 'key_signature':
                feat_dict[msg.type] = msg.key
            elif msg.type == 'set_tempo':
                feat_dict['tempo'] = msg.tempo
    return feat_dict


def print_tick2seconds(midiFile, tempo):
    for i, track in enumerate(midiFile.tracks):
        print('Track {}:'.format(i))
        for msg in track:
            if not msg.is_meta:
                ''' print('  {!r}'.format(message))'''
                if msg.type == 'note_on':
                    time_in_secs = mido.tick2second(msg.time, midiFile.ticks_per_beat, tempo)
                    print('{!r} -- time in secs: {}'.format(msg, time_in_secs))

                elif msg.type == 'note_off':
                    print('\n')
                    time_in_secs = mido.tick2second(msg.time, midiFile.ticks_per_beat, tempo)
                    print('{!r} -- time in secs: {}'.format(msg, time_in_secs))
        print('\n')


def note_mapper(note_value):
    octave = math.floor((note_value / 12) - 1)
    notes = 'C{0},C#{0}/Db{0},D{0},D#{0}/Eb{0},E{0},F{0},F#{0}/Gb{0},G{0},G#{0}/Ab{0},A{0},A#{0}/Bb{0},B{0}'.format(octave).split(',')

    note = notes[(note_value % 12)]
    # print(note.lower())
    return(note.lower())


def play_midi_no_feedback(midiFile):

    for msg in midiFile.play():
        print(msg)
        # time.sleep(1)
        if msg.type=='note_on' or msg.type=='note_off':
            led = ledmap.get(note_mapper(msg.note)[0], -1)
            if led == -1:
                for note, led in ledmap.items():
                    led.off()
            else:
                if msg.type == 'note_on':
                    time.sleep(.07)

                led.toggle()


def play_midi(midiFile):

    for msg in midiFile.play():
        print(msg)
        if msg.type=='note_on' or msg.type=='note_off':
            led = ledmap.get(note_mapper(msg.note)[0], -1)
            if led == -1:
                for note, led in ledmap.items():
                    led.off()
            else:
                if msg.type == 'note_on':
                    time.sleep(.04)

                led.toggle()
                if msg.type == 'note_on':
                    with mido.open_input('MPKmini2') as inport:
                        for k_msg in inport:
                            if note_mapper(k_msg.note) == note_mapper(msg.note):
                                break



filename = os.path.join('../midi_files', args.midi_file)

"""
Open a MIDI file and get the tempo and ticks per beat info.
"""
midiFile = MidiFile(filename)
TICKS_PER_BEAT = midiFile.ticks_per_beat
TEMPO = get_midi_tempo(midiFile)
print('ticks_per_beat = {}, tempo = {} \n'.format(TICKS_PER_BEAT, TEMPO))

print('song name: {}'.format(midiFile.filename.split('/')[-1]))


print('\n')
try:
    play_midi_no_feedback(midiFile)
    while True:
        play_midi(midiFile)
except:
    for note, led in ledmap.items():
        led.off()
    print('\n Thanks for playing! You got this!')









