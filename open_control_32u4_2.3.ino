

#include <Bounce2.h>
#include <EEPROM.h>
#include <ResponsiveAnalogRead.h>
#include <FastLED.h>
#include <USB-MIDI.h>

 USBMIDI_CREATE_DEFAULT_INSTANCE();
 // MIDI_CREATE_INSTANCE(HardwareSerial, Serial1, MIDI_DIN);

bool usb_midi = HIGH;
byte const NUM_LAYOUT = 3;
byte current_layout = 0;

byte const NUM_POTS = 2;

byte const NUM_BUTTONS = 6;

int matrix_brightness = 0;

#define NUM_LEDS 6
CRGB leds[NUM_LEDS];
int BRIGHTNESS = 50;
#define LED_TYPE WS2812
#define COLOR_ORDER GRB

bool MIDI_Mode = LOW; // MIDI_Mode == 0 mirrors USB_MIDI, MIDI_Mode == 1 enables external MIDI control

unsigned long blinking_speed = 500;

const int b_pins[NUM_BUTTONS] = {11, 3, 2, 9, 10, 5};
#define LED_PIN A2
const int a_pins[NUM_POTS] = {A1, A0};
#define data_Row 8
#define latch_Row 12          // row
#define clock_Row 4          // row
#define toggle_Row 6          // row
#define latch_Col A4          // coln
#define clock_Col A3          // coln
#define data_Col A5           // coln
#define toggle_Col 13         // coln
