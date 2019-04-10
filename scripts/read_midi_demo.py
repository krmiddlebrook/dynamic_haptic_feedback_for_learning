import mido
from mido import Message, MidiFile, MidiTrack
import time
import sys
import json



# print(mido.get_input_names())
# print(mido.get_output_names())

inport = mido.open_input('MPKmini2')
# outport = mido.open_outport()
TEMPO = mido.bpm2tempo(100) # express bpm in microseconds per beat for mido
sys.stdout.write("default tempo = {}\n".format(TEMPO))


def get_midi_tempo(midiFile):
    for i, track in enumerate(midi_file.tracks):
        sys.stdout.write('=== Track {}\n'.format(i))
        for message in track:

            if message.is_meta:
                if message.type == 'set_tempo':
                    tempo = message.tempo
                    sys.stdout.write('found track tempo! \n')
            elif not message.is_meta:
                sys.stdout.write('  {!r}\n'.format(message))
    return tempo


def midifile_to_dict(mid):
    tracks = []
    for track in mid.tracks:
        tracks.append([vars(msg).copy() for msg in track])

    midi_dict = dict({'ticks_per_beat': mid.ticks_per_beat,
                      'tracks': tracks
                      })
    return  midi_dict


"""
Read MIDI file.:
    Ex: python read_midi_demo.py 'test_track.mid'
"""
# filename = sys.argv[1]
filename = 'test_track.mid'

"""
Open a MIDI file and get the tempo and ticks per beat info.
"""
midi_file = MidiFile(filename)
TICKS_PER_BEAT = midi_file.ticks_per_beat
TEMPO = get_midi_tempo(midi_file)
sys.stdout.write('ticks_per_beat = {}, tempo = {} \n'.format(TICKS_PER_BEAT, TEMPO))

midi_dict = midifile_to_dict(midi_file)
sys.stdout.write(str(midi_dict))


# with mido.open_output('MPKmini2') as outport:
#     for msg in inport:
#
#         if msg.type == 'note_on':
#             start = time.time()
#             # print(start)
#         if msg.type == 'note_off':
#             dur = time.time() - start
#             num_ticks = round(mido.second2tick(second=dur, ticks_per_beat=TICKS_PER_BEAT, tempo=TEMPO))
#             msg.time = num_ticks
#             print("new message " + str(msg))
#             outport.send(msg)
        # 	print('you played the correct notes')
        # 	print('you played note: ' + str(msg.note))

# outport.close()