/*
  Blink without Delay

  Turns on and off a light emitting diode (LED) connected to a digital pin,
  without using the delay() function. This means that other code can run at the
  same time without being interrupted by the LED code.

  The circuit:
  - Use the onboard LED.
  - Note: Most Arduinos have an on-board LED you can control. On the UNO, MEGA
    and ZERO it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN
    is set to the correct LED pin independent of which board is used.
    If you want to know what pin the on-board LED is connected to on your
    Arduino model, check the Technical Specs of your board at:
    https://www.arduino.cc/en/Main/Products

  created 2005
  by David A. Mellis
  modified 8 Feb 2010
  by Paul Stoffregen
  modified 11 Nov 2013
  by Scott Fitzgerald
  modified 9 Jan 2017
  by Arturo Guadalupi

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/BlinkWithoutDelay
*/
#include <assert.h>
#define BPM 120.0

const int BPS = BPM / 60.0 * 1000;

const float restRat = 0.9;

#define foreach(item, array) \
    for(int keep = 1, \
        count = 0,\
        size = sizeof (array) / sizeof *(array); \
        keep && count != size; \
        keep = !keep, count++) \
      for(item = (array) + count; keep; keep = !keep)
// constants won't change. Used here to set a pin number:
const int ledPin =  LED_BUILTIN;
const int indexPin = 3;
const int middlePin = 4;
const int ringPin = 5;
const int pinkyPin = 6;

// Variables will change:
int ledState = LOW;             // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

// constants won't change:
const long interval = 1000;           // interval at which to blink (milliseconds)

int ledPointer = indexPin;

typedef enum {
  E = indexPin,
  D,
  C,
  B,
  R = ledPin
} notes;

void setup() {
  Serial.begin(9600);
  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);
  pinMode(indexPin, OUTPUT);
  pinMode(middlePin, OUTPUT);
  pinMode(ringPin, OUTPUT);
  pinMode(pinkyPin, OUTPUT);
}

void playNote(int n, float dur) {
  int note = dur * BPS * (restRat);
  int rest = dur * BPS - note;
  digitalWrite(n, HIGH);
  delay(note);
  digitalWrite(n, LOW);
  delay(rest);
}

void loop() {
  notes song[] = {E, D, C, D, E, E, E,
                  D, D, D, R, E, E, E,
                  E, D, C, D, E, E, E, E,
                  D, D, E, D, C
                 };

  float beats[] = {0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5,
                   0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5,
                   0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
                   0.25, 0.25, 0.25, 0.25, 1
                  };
  assert(sizeof(song) / sizeof(song[0]) == sizeof(beats) / sizeof(beats[0]));
  for (int i = 0; i < sizeof(song) / sizeof(song[0]); i++) {
    playNote((int)song[i], beats[i]);
  }
  delay(2500);
  // set the LED with the ledState of the variable:
  ledPointer++;
  if (ledPointer > pinkyPin) {
    ledPointer = indexPin;
  }
}
