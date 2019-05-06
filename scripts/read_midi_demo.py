import mido
import math
import pandas as pd
import numpy as np
import time
import argparse

parser = argparse.ArgumentParser(description='Program to capture midi input')
parser.add_argument('midi_file', help='the name of the midi file that will be attempted')
parser.add_argument('username', help='the name of the user')
parser.add_argument('attempt', type=int, help='enter which attempt # this will be for the user')
args = parser.parse_args()

TEMPO = mido.bpm2tempo(100) # express bpm in microseconds per beat for mido



def note_mapper(note_value):

    octave = math.floor((note_value / 12) - 1)
    notes = 'C{0},C#{0}/Db{0},D{0},D#{0}/Eb{0},E{0},F{0},F#{0}/Gb{0},G{0},G#{0}/Ab{0},A{0},A#{0}/Bb{0},B{0}'.format(octave).split(',')

    note = notes[(note_value % 12)]
    # print(note.lower())
    return(note.lower())

def convert_performance_to_df(notes):
    '''
    a function to create a dataframe containing the user's performance and then saves it to a csv file
    :param notes: an array of arrays where each array contains information about the a note the user played. Each nest
     array must have the following information: [msg.type, msg.note, msg.velocity, msg.time]
    :return: user_data: a dataframe containing the user's performance
    '''

    output_filename = '../user_studies/' + args.username + "_" + str(args.attempt) + "_" + args.midi_file + '.csv'
    notes[0][3] = 0  # set the time value of the first note to 0
    user_data = pd.DataFrame(np.array(notes),
                             columns=['note_type', 'note', 'velocity', 'time'])  # save the user's performance
    user_data.to_csv(output_filename, index=False)  # write user's performance to a csv file
    return user_data

def read_midi_input():
    '''
    a function to capture the user's midi performance and return it as a dataframe
    :return: user_data: a dataframe containing the user's performance
    '''

    notes_played = []
    finished = False
    inport = mido.open_input('MPKmini2')
    while not finished:
        t1 = time.time()
        for msg in inport:
            t2 = time.time()
            if msg.type == 'note_on':
                if msg.note == 44: # if the note is 44, reset and rerun the function
                    inport.close()
                    print("\n ==========Your performance was successfully reset. You got this!========== \n")
                    read_midi_input()
                elif msg.note == 47:
                    finished = True
                    break
                else:
                    notes_played.append([msg.type, msg.note, msg.velocity, t2 - t1])
                    print('type: {}, note: {}, velocity: {}, time: {}'.format(msg.type, int(msg.note),
                                                                              int(msg.velocity), t2 - t1))
            t1 = t2
    inport.close()
    user_data = convert_performance_to_df(notes_played) # convert performance to dataframe and write it to csv file
    print('Great performance! Thanks for participating! \n') # thank the participant
    return user_data



read_midi_input()


# notes_played = []
# try:
#     with mido.open_input('MPKmini2') as inport:
#         t1 = time.time()
#         for msg in inport:
#             # print(msg)
#             t2 = time.time()
#             if msg.type == 'note_on':
#                 notes_played.append([msg.type, msg.note, msg.velocity, t2-t1])
#                 print('type: {}, note: {}, velocity: {}, time: {}'.format(msg.type, int(msg.note), int(msg.velocity), t2-t1))
#             t1 = t2
#
# except KeyboardInterrupt:
#     print('\n')
#     print('Great attempt! Thanks for participating!')
#     notes_played[0][3] = 0
#     user_data = pd.DataFrame(np.array(notes_played), columns=['note_type', 'note', 'velocity', 'time']) # save the user's performance
#     user_data.to_csv(output_filename, index=False) # write user's performance to a csv file




