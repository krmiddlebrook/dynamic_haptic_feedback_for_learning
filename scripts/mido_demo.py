import mido
from mido import Message, MidiFile, MidiTrack
import time



print(mido.get_input_names())
# print(mido.get_output_names())

inport = mido.open_input('MPKmini2')
# outport = mido.open_outport()
TEMPO = mido.bpm2tempo(95) # express bpm in microseconds per beat for mido
TICKS_PER_BEAT = 3

with mido.open_output('MPKmini2') as outport:
    for msg in inport:

        if msg.type == 'note_on':
            start = time.time()
            # print(start)
        if msg.type == 'note_off':
            dur = time.time() - start
            num_ticks = round(mido.second2tick(second=dur, ticks_per_beat=TICKS_PER_BEAT, tempo=TEMPO))
            msg.time = num_ticks
            print("new message " + str(msg))
            outport.send(msg)
        # 	print('you played the correct notes')
        # 	print('you played note: ' + str(msg.note))

outport.close()

