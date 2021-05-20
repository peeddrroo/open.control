long unsigned _now = millis();
byte ticker = 0;
byte but = 0;
byte ana = 0;

void set_led_matrix() {
  pinMode(latch_Col, OUTPUT);
  pinMode(clock_Col, OUTPUT);
  pinMode(data_Col, OUTPUT);
  pinMode(latch_Row, OUTPUT);
  pinMode(clock_Row, OUTPUT);
  pinMode(data_Row, OUTPUT);
  pinMode(toggle_Col, OUTPUT);
  pinMode(toggle_Row, OUTPUT);

}

void set_LEDs() {
  pinMode(LED_PIN, OUTPUT);
  FastLED.addLeds<LED_TYPE , LED_PIN, GRB>(leds, NUM_LEDS); // for GRB LEDs
  FastLED.setBrightness(BRIGHTNESS);
  byte init_led_color_red[NUM_LEDS] = {80, 0, 17, 100, 124, 90};
  byte init_led_color_green[NUM_LEDS] = {0, 78, 23, 100, 49, 0};
  byte init_led_color_blue[NUM_LEDS] = {127, 46, 80, 0, 0, 12};
  for ( byte i = 0; i < NUM_LEDS; i += 1) {
    l[i].num = i;
    l[i].r = init_led_color_red[i];
    l[i].g = init_led_color_green[i];
    l[i].b = init_led_color_blue[i];
    l[i].led_update(LOW);
  }
}

void set_EEPROM() {
  for (byte layout_num = 0; layout_num < NUM_LAYOUT; layout_num++) {
    for (byte i = 0; i <= 22; i++) {
      byte type = EEPROM.read(layout_num * 100 + i);
      byte control = EEPROM.read(layout_num * 100 + i + 30);
      byte channel = EEPROM.read(layout_num * 100 + i + 60);
      if (i < 6 && control != 255) {
        b[i].short_control[layout_num] = control;
        b[i].short_ch[layout_num] = channel;
        b[i].short_type[layout_num] = type;
      }
      if (6 <= i && i < 12 && control != 255) {
        b[i - 6].long_control[layout_num] = control;
        b[i - 6].long_ch[layout_num] = channel;
        b[i - 6].long_type[layout_num] = type;
      }
      if (12 <= i && i < 18 && control != 255) {
        l[i - 12].control[layout_num] = control;
        // l[i - 12].state[layout_num] = channel;
      }
      if (18 <= i && i < 22 && control != 255) {
        a[i - 18].control[layout_num] = control;
        a[i - 18].channel[layout_num] = channel;
      }
      if (i == 22 && control != 255) {
        disp.layout[layout_num] = control;
      }
    }
  }
  for (byte i = 0; i < 2; i++) {
    if (EEPROM.read(300 + i) != 255) {
      byte sysex_array[8] = {240, 122, 29, 1, 19, 80 + i, EEPROM.read(300 + i), 247};
      // MIDI_DIN.sendSysEx(8, sysex_array, true);
      MIDI.sendSysEx(8, sysex_array, true);
    }
  }
  if (EEPROM.read(298) != 255) BRIGHTNESS = EEPROM.read(298);
  if (EEPROM.read(299) != 255) matrix_brightness = EEPROM.read(299);
}


void setup() {

  MIDI.begin(MIDI_CHANNEL_OMNI);
  MIDI.turnThruOff();
  MIDI.setHandleSystemExclusive(onSysEx);
  MIDI.setHandleControlChange(onControlChange);
  set_LEDs();
  set_EEPROM();
  set_led_matrix();
  disp.build_text(12);
}
byte sysex_data[15];
byte cc_data[3];
byte sysex_index = 0;
byte cc_index = 0;
bool sysex_in = LOW;
bool cc_in = LOW;
bool booting = HIGH;

void loop() {
  
  b[but].update_button();
  a[ana].check_pot();
/*

  if (booting) {
    if (b[0].held == HIGH) {
      usb_midi = LOW;
      Serial1.begin(31250);
    }
booting = LOW;
  }*/
  if (usb_midi) MIDI.read();
  /*
  else {
    if (Serial1.available()) {
      if (usb_midi) usb_midi = LOW;
      byte inByte = Serial1.read();
      //  MIDI.sendControlChange(inByte-100, inByte, 5);
      if (inByte == 240) {
        sysex_in = HIGH;
      }

      if (inByte >= 176 && inByte <= 191 && !sysex_in) {
        cc_in = HIGH;
      }

      if (sysex_in && !cc_in) {
        sysex_data[sysex_index] = inByte;
        sysex_index++;
        if (inByte == 247) {
          sysex_index = 0;
          sysex_in = LOW;
          onSysEx(sysex_data);
        }
      }

      if (cc_in && !sysex_in) {
        //  MIDI.sendControlChange(inByte, midi_index, 3);
        cc_data[cc_index] = inByte;
        cc_index++;
        if (cc_index == 3) {
          onControlChange(cc_data[0] - 175, cc_data[1], cc_data[2]);
          cc_index = 0;
          cc_in = LOW;
        }
      }
    }
  }*/

  disp.tick_off();
  disp.show_char(ticker);
  disp.tick_on();

  but ++;
  ana ++;
  ticker++;

  if (but == NUM_BUTTONS) but = 0;
  if (ana == NUM_POTS) ana = 0;
  if (ticker == 32) ticker = 0;

  if (millis() - _now > blinking_speed / 2) {
    disp.inc_scroll();
    for (byte i = 0; i < NUM_LEDS; i++) {
      l[i].toggle_led();
      _now = millis();
    }
  }

}
