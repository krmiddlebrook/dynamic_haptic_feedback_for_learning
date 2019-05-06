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

#
parser = argparse.ArgumentParser(description='Haptic Glove Piano Learning App')
parser.add_argument('midi_file', help='the name of the midi file that will be attempted', required=True)
parser.add_argument('username', help='the name of the user', required=True)
parser.add_argument('attempt', type=int, help='enter which attempt # this will be for the user', required=True)
args = parser.parse_args()


class HapticGlove:
    '''
    a class to interact with the haptic glove and record user data
    '''
    def __init__(self, args):
        self.args = args
        self.midiFile = MidiFile(os.path.join('../midi_files', args.midi_file))
        self.board = Arduino()
        self.notemap = {'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6}
        self.ledmap = {k: Led(self.board, v) for (k, v) in self.notemap.items()}
        print("COnnectedt to Glove")

    def note_mapper(self, note_value):
        '''
        converts note value (int) to key at octave (string)
        :param: note_value: the midi note value (an int between 1 and 128)
        :return: the key and octave of the note
        '''
        octave = math.floor((note_value / 12) - 1)
        notes = 'C{0},C#{0}/Db{0},D{0},D#{0}/Eb{0},E{0},F{0},F#{0}/Gb{0},G{0},G#{0}/Ab{0},A{0},A#{0}/Bb{0},B{0}'.format(
            octave).split(',')

        note = notes[(note_value % 12)]
        return note.lower()

    def play_midi_no_feedback(self):
        '''
        a function to play output a static performance of the midi file to the glove
        :return:
        '''
        for msg in self.midiFile.play():
            print(msg)
            if msg.type == 'note_on' or msg.type == 'note_off':
                led = self.ledmap.get(self.note_mapper(msg.note), -1)
                if led == -1:
                    for note, led in self.ledmap.items():
                        led.off()
                else:
                    if msg.type == 'note_on':
                        time.sleep(.07)
                    led.toggle()

    def play_midi(self):
        '''
        a function to play a dynamic performance of the midi file to the glove
        '''
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

    def convert_performance_to_df(self, notes):
        '''
        a function to create a dataframe containing the user's performance and then saves it to a csv file
        :param notes: an array of arrays where each array contains information about the a note the user played. Each nested
                      array must have the following information: [msg.type, msg.note, msg.velocity, msg.time]
        :return: user_data: a dataframe containing the user's performance
        '''
        self.userfile = '../user_studies/' + self.args.username + "_" + str(self.args.attempt) + "_" + self.args.midi_file + '.csv'
        notes[0][3] = 0  # set the time value of the first note to 0
        user_data = pd.DataFrame(np.array(notes),
                                 columns=['note_type', 'note', 'velocity', 'time'])  # save the user's performance
        user_data.to_csv(self.userfile, index=False)  # write user's performance to a csv file

        return user_data


    def read_midi_input(self):
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
        self.user_data = self.convert_performance_to_df(notes_played)  # convert performance to dataframe and write it to csv file
        print('Great performance! Thanks for participating! \n')  # thank the participant

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


    def get_playing_accuracy(self):
        '''
        :return: error_score: the total number of error between the user's attempt and the actual note sequence (calculated using DTW algorithm)
        '''
        self.midi_df = self.make_midi_df()  # create a dataframe for the midifile containing the correct note sequence information

        user_notes = self.user_data['note'].astype(int).values
        midi_notes = self.midi_df['note'].astype(int).values

        # print('user notes: {}\n'.format(user_notes))
        # print('correct notes: {} \n'.format(midi_notes))

        error, path = fastdtw(user_notes, midi_notes, dist=hamming)  # compute the number of error notes
        print('Total number of errors: {}'.format(error))
        self.error = error


def main(args):
    glove = HapticGlove(args)