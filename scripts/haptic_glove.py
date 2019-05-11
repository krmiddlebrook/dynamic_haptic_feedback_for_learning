import mido
from mido import Message, MidiFile, MidiTrack
import math
import pandas as pd
import numpy as np
import time
import argparse
from fastdtw import fastdtw
from scipy.spatial.distance import hamming # import the distance metric we will use
import os
from BreakfastSerial import Arduino, Led

# args to pass to program: midi file, username, attempt
parser = argparse.ArgumentParser(description='A Haptic Glove Piano Learning App')
parser.add_argument('midi_file', help='the name of the midi file that will be attempted')
parser.add_argument('username', help='the name of the participant')
parser.add_argument('attempt', type=int, help='enter which attempt # this will be for the participant')
args = parser.parse_args()


class HapticGlove:
    '''
    a class to interact with the haptic glove and record user data
    '''
    def __init__(self, args, board, notemap, ledmap):
        self.args = args
        self.midiFile = MidiFile(os.path.join('../midi_files', args.midi_file))
        self.board = board
        self.notemap = notemap
        self.ledmap = ledmap

    def note_mapper(self, note_value):
        '''
        converts note value (int) to key at octave (string)
        Args:
            note_value: the midi note value (an int between 1 and 128)
        :return: the key and octave of the note
        '''
        octave = math.floor((note_value / 12) - 1)
        notes = 'C{0},C#{0}/Db{0},D{0},D#{0}/Eb{0},E{0},F{0},F#{0}/Gb{0},G{0},G#{0}/Ab{0},A{0},A#{0}/Bb{0},B{0}'.format(
            octave).split(',')

        note = notes[(note_value % 12)]
        return(note.lower())

    def play_midi_no_feedback(self):
        '''Maps MIDI to glove and uses PHL system'''
        try:
            while True:
                for msg in self.midiFile.play():
                    print(msg)
                    if msg.type == 'note_on' or msg.type == 'note_off':
                        led = self.ledmap.get(self.note_mapper(msg.note)[0], -1)
                        if led == -1:
                            for note, led in self.ledmap.items():
                                led.off()
                        else:
                            if msg.type == 'note_on':
                                time.sleep(.04)
                            led.toggle()
        except:
            for note, led in self.ledmap.items():
                led.off()
            print('Finished PHL lesson. Good job!')

    def play_midi(self):
        ''' Maps MIDI to glove and uses AHL assistant'''
        try:
            while True:
                for msg in self.midiFile.play():
                    print(msg)
                    if msg.type == 'note_on' or msg.type == 'note_off':
                        led = self.ledmap.get(self.note_mapper(msg.note)[0], -1)
                        if led == -1:
                            for note, led in self.ledmap.items():
                                led.off()
                        else:
                            if msg.type == 'note_on':
                                time.sleep(.04)
                            led.toggle()
                            if msg.type == 'note_on':
                                with mido.open_input('MPKmini2') as inport:
                                    for k_msg in inport:
                                        if self.note_mapper(k_msg.note) == self.note_mapper(msg.note):
                                            break
        except:
            for note, led in self.ledmap.items():
                led.off()
            print('Finished AHL lesson. Good job!')

    def convert_performance_to_df(self, notes):
        '''
        a helper function for read_midi_input to create a dataframe containing the user's performance
        and then saves it to a csv file
        Args:
            notes: an array of arrays where each array contains information about the a note the user played.
            Each nested array must have the following information: [msg.type, msg.note, msg.velocity, msg.time]
        :return:
                user_data: a dataframe containing the user's performance
        '''
        self.userfile = '../user_studies/' + self.args.username + "_" + str(self.args.attempt) + "_" + self.args.midi_file + '.csv'
        notes[0][3] = 0  # set the time value of the first note to 0
        user_data = pd.DataFrame(np.array(notes),
                                 columns=['note_type', 'note', 'velocity', 'time'])  # save the user's performance
        user_data.to_csv(self.userfile, index=False)  # write user's performance to a csv file

        return user_data


    def read_midi_input(self):
        '''
        function to capture the user's MIDI performance
        :return:
                user_perf: a dataframe containing the user's performance data
        '''
        notes_played = []
        finished = False
        print('You may start playing now.')
        inport = mido.open_input('MPKmini2')
        while not finished:
            t1 = time.time()
            for msg in inport:
                t2 = time.time()
                if msg.type == 'note_on':
                    if msg.note == 44:  # if the note is 44, reset and rerun the function
                        inport.close()
                        print("\n ==========Your performance was successfully reset. You got this!========== \n")
                        self.read_midi_input()
                    elif msg.note == 47:
                        finished = True
                        break
                    else:
                        notes_played.append([msg.type, msg.note, msg.velocity, t2 - t1])
                        print('type: {}, note: {}, velocity: {}, time: {}'.format(msg.type, int(msg.note),
                                                                                  int(msg.velocity), t2 - t1))
                t1 = t2
        inport.close()
        user_perf = self.convert_performance_to_df(notes_played)  # convert performance to dataframe and write it to csv file
        print('Great performance! \n')  # a little encouragement never hurts :)
        return user_perf

    def make_midi_df(self):
        '''
        creates a dataframe for the midi file
        :return: a pandas dataframe containing the midi note sequence
        '''
        midi_notes = []  # make a data frame to store the correct note sequence
        for msg in self.midiFile:
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
    board = Arduino() # connect to the Arduino (Haptic Glove)
    print("COnnectedt to Haptic Glove!")
    notemap = {'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6}
    ledmap = {k: Led(board, v) for (k, v) in notemap.items()}
    glove = HapticGlove(args, board, notemap, ledmap) # create instance of haptic glove

    perf_acc = [] # list to store performance accuracy after each performance
    midi_perf = glove.make_midi_df() # the ground truth MIDI performance

    # 1st performance
    haptic_lesson = False
    while True:
        ready_for_p1 = raw_input('Ready for your 1st performance attempt? [y/n]: ')
        if ready_for_p1 == 'y':
            u_perf1 = glove.read_midi_input() # read and save the user's 1st MIDI performance, before PHL/AHL
            perf1_acc = glove.get_playing_accuracy(midi_perf, u_perf1) # measure performance accuracy before PHL/AHL
            perf_acc.append(perf1_acc) # add performance 1 error to performance accuracy list
            haptic_lesson = True
            break

    # begin haptic lesson
    begin_p2 = False
    lesson_type = ''
    while haptic_lesson:
        ready_for_haptic = raw_input('Ready for haptic lesson? (y/n): ')
        if ready_for_haptic == 'y':
            glove.play_midi()  # learn MIDI sequence with AHL assistance
            lesson_type = 'AHL'
            haptic_lesson = False
            begin_p2 = True

    # 2nd performance
    if begin_p2:
        while True:
            ready_for_p2 = raw_input('Ready for your 2nd performance attempt? (y/n):')
            if ready_for_p2 == 'y':
                u_perf2 = glove.read_midi_input()  # read and save the user's 2nd MIDI performance, after PHL/AHL
                perf2_acc = glove.get_playing_accuracy(midi_perf,
                                                       u_perf2)  # measure performance accuracy after PHL/AHL
                perf_acc.append(perf2_acc)  # add performance 2 error to performance accuracy list
                break

    # save results
    improve_score = perf_acc[0] - perf_acc[1] # difference in error score before and after haptic lesson
    perf_data = [args.username, args.midi_file, perf_acc[0], perf_acc[1], improve_score, lesson_type]  # format study data for csv
    print(perf_data)
    print('saving study data...\n')  # save accuracy metrics
    if os.path.exists('../users_performance_data.csv'):
        perf_data = pd.DataFrame([perf_data], columns=['participant', 'midi_file', 'p1_error', 'p2_error', 'improve_score', 'lesson_type'])
        perf_data.to_csv('../users_performance_data.csv', header=False, index=False, mode='a')  # append new data to csv
    else:
        perf_data = pd.DataFrame([perf_data], columns=['participant', 'midi_file', 'p1_error', 'p2_error', 'improve_score', 'lesson_type'])
        perf_data.to_csv('../users_performance_data.csv', index=False)  # create and save data to csv

    print('p1 error: {}, p2 error: {}, improvement score: {}'.format(perf_acc[0], perf_acc[1], improve_score))
    print('Study complete. Great job! Thank you for participating!\n')




main()