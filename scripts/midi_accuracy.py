import numpy as np
from fastdtw import fastdtw
from mido import MidiFile
import pandas as pd
import time
from scipy.spatial.distance import hamming # import the distance metric we will use


# user file vs real midi file

def make_midi_df(midifile):
    '''

    :param midifile: the name of the midifile
    :return: a pandas dataframe containing the midi note sequence
    '''
    midi_notes = []  # make a data frame to store the correct note sequence
    for msg in MidiFile('../midi_files/'+midifile):

        if msg.type == 'note_on':
            midi_notes.append([msg.type, int(msg.note), int(msg.velocity), float(msg.time)])

    return pd.DataFrame(np.array(midi_notes), columns=['note_type', 'note', 'velocity', 'time'])

def get_playing_accuracy(userfile, midifile):
    '''
    :param userfile: the name of the user file
    :param midifile: the name of the midifile
    :return: error_score: the total number of error between the user's attempt and the actual note sequence (calculated using DTW algorithm)
    '''
    user_data = pd.read_csv('../user_studies/'+userfile) # read user's midi data file
    midi_df = make_midi_df(midifile) # create a dataframe for the midifile containing the correct note sequence information

    user_notes = user_data['note'].astype(int).values
    midi_notes = midi_df['note'].astype(int).values

    # print('user notes: {}\n'.format(user_notes))
    # print('correct notes: {} \n'.format(midi_notes))

    error, path = fastdtw(user_notes, midi_notes, dist=hamming) # compute the number of error notes
    print('Total number of errors: {}'.format(error))

    return error



get_playing_accuracy('kai_2_simple_final_mary.csv', 'simple_final_mary.mid')
print('===========THe End============= \n')



