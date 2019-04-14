'''
Reads midi file and then maps track info to haptic glove
'''

import mido
from mido import Message, MidiFile, MidiTrack
import time
import sys
import json
import pprint
import math
from threading import Timer


from BreakfastSerial import Arduino, Led
from time import sleep


# print(mido.get_input_names())
# print(mido.get_output_names())

# inport = mido.open_input('MPKmini2')
# outport = mido.open_outport()
TEMPO = mido.bpm2tempo(100) # expresses bpm in microseconds per beat for mido
print("default tempo = {}\n".format(TEMPO))
board = Arduino()
print("COnnectedt")

notemap = {'e':3, 'd':4, 'c':5, 'b':6}
ledmap = {k:Led(board, v) for (k,v) in notemap.items()}


def get_midi_tempo(midiFile):
    for i, track in enumerate(midiFile.tracks):
        print('Track {}:'.format(i))
        for msg in track:

            if msg.is_meta:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
            elif not msg.is_meta:
                print('  {!r}'.format(msg))
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




def play_midi(midiFile):

    for msg in midiFile.play():
        # print(msg)
        if msg.type=='note_on' or msg.type=='note_off':
            # print(msg)
            led = ledmap.get(note_mapper(msg.note)[0], -1)
            if led == -1:
                for note, led in ledmap.items():
                    led.off()
            else:
                if msg.type == 'note_on':
                    time.sleep(.25/10)

                led.toggle()


# filename = sys.argv[1]
filename = '/Users/kaimiddlebrook/Documents/GitHub/dynamic_haptic_feedback_for_learning/mary_had_a_little_lamb.mid'

"""
Open a MIDI file and get the tempo and ticks per beat info.
"""
midiFile = MidiFile(filename)
TICKS_PER_BEAT = midiFile.ticks_per_beat
TEMPO = get_midi_tempo(midiFile)
print('ticks_per_beat = {}, tempo = {} \n'.format(TICKS_PER_BEAT, TEMPO))
pprint.pprint(midiFile.print_tracks())

# midi_dict = midifile_to_dict(midi_file)
# print(str(midi_dict))
print('song name: {}'.format(midiFile.filename))
# pprint.pprint(get_track_features(midiFile))
# print_tick2seconds(midiFile, TEMPO)

print('\n')
# midiFile.print_tracks()
play_midi(midiFile)













