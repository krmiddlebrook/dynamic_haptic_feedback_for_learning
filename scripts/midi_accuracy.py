import numpy as np
from fastdtw import fastdtw
from mido import MidiFile
import pandas as pd
import time
from scipy.spatial.distance import hamming # import the distance metric we will use
import os

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

def get_playing_accuracy(self, p1, p2):
    '''
    function to measure MIDI performance accuracy after PHL/AHL
    Args:
        p1: (dataframe columns=['note_type', 'note', 'velocity', 'time']) a MIDI performance
        p2: (dataframe columns=['note_type', 'note', 'velocity', 'time']) a MIDI performance
    :return:
            error: total number of errors between two MIDI note sequences
                   (calculated using DTW hamming algorithm)
    '''

    p1_notes = p1['note'].astype(int).values
    p2_notes = p2['note'].astype(int).values

    error, path = fastdtw(p1_notes, p2_notes, dist=hamming)  # compute the number of errors
    print('Total number of errors: {}'.format(error))
    return error




def main():


    improve_score = perf_acc[0] - perf_acc[1]  # difference in error score before and after haptic lesson
    perf_data = [args.username, args.midi_file, perf_acc[0], perf_acc[1], improve_score,
                 lesson_type]  # format study data for csv
    print(perf_data)
    print('saving study data...\n')  # save accuracy metrics
    if os.path.exists('../users_performance_data.csv'):
        perf_data = pd.DataFrame([perf_data],
                                 columns=['participant', 'midi_file', 'p1_error', 'p2_error', 'improve_score',
                                          'lesson_type'])
        perf_data.to_csv('../users_performance_data.csv', header=False, index=False, mode='a')  # append new data to csv
    else:
        perf_data = pd.DataFrame([perf_data],
                                 columns=['participant', 'midi_file', 'p1_error', 'p2_error', 'improve_score',
                                          'lesson_type'])
        perf_data.to_csv('../users_performance_data.csv', index=False)  # create and save data to csv

    print('p1 error: {}, p2 error: {}, improvement score: {}'.format(perf_acc[0], perf_acc[1], improve_score))
    print('Study complete. Great job! Thank you for participating!\n')


