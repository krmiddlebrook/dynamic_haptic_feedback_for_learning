# Haptic Glove: An Active Haptic Learning System to learn how to play the piano.
A program that uses a custom made Active Haptic Learning (AHL) system to teach users how to play songs on the piano.

## Requirments
- Packages:
  1. Python 2.7
  2. mido
  3. pandas
  4. numpy
  5. fastdtw
  6. BreakfastSerial
  7. Node
  8. express
  9. 
- Hardware & Materials:
 1. Arduino Nano
 2. 5 disk motors
 3. Glove
 4. MIDI controller


## Running the code
1. Connect the haptic glove to the computer via USB
2. Connect the MIDI controller to the computer via USB
3. Navigate to the directory where you stored the code
4. Run: ```python haptic_glove.py midi_file.mid participant_name attempt_number```

## What's going on under the hood?
Once you've installed and built all the necessary dependencies and hardware, you can run ```python haptic_glove.py midi_file.mid participant_name attempt_number```. The code in `haptic_glove.py` expects 3 arguments from the command-line: 
1. midi_file.mid = the name of the midi file you want to map to the glove. This MIDI file will also be the ground truth performance
2. particapant_name = the name of the participant that will be wearing the glove and performing
3. attempt = the attempt number for the specific participant. The attempt number for each particapant starts at 1. For example, if it is the first time particapant A takes the study, their attempt number will be 1. 

After these command-line arguments are read, the program will connect to the Arduino Nano that is connected to the haptic glove. Then the program will read in the MIDI file and store it as a pandas dataframe for later processing. Then the program will ask the user if they are ready to begin their first performance. Once they enter 'y' (e.g. yes), the program is ready to read and store the user's first performance. When the user is done with their first performance, they can press the key that corresponds to note 47 on the MIDI controller to end the the performance and save it. Next, the program asks the user if they are ready to begin their active haptic learning session (AHL). Once the user enters 'y' (e.g. yes), the haptic lesson will begin. To end the lesson, simply press control-c. After the lesson, the program will ask the user if they are ready to play their second performance. Once the user enters 'y' (e.g. yes), the program is ready to read the user's MIDI performance. When the user is finished performing, they can press the key that corresponds to note 47 on the MIDI controller to end the the performance and save it. Finally, the program will calculate the performance metrics for each of the user's performances and then append this data to the csv file `users_performance_data.csv`. If this file does not exist, it will be created by the program. Once this process is done, the error score after both the first and second performances will be printed to the console along with the improvement score (e.g. the difference in the error score between the first and second performance). Then the program ends. 


