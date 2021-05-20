// 0 -> 5 : Buttons Short
// 6 -> 11 : Buttons Long
// 12 -> 17 : Leds
// 18 -> 21 : Analog

// prefix = {240, 122, 29, 1, 19};
// data[5] :
//           69 -> receive Live acknowledgement
//           70 -> receive Short Buttons Data
//           71 -> receive Long Buttons Data
//           72 -> receive Led Data
//           73 -> receive Analog Data
//           74 -> receive Dump Request
//           75 -> receive Layout change
//           76 -> receive Disconnect
//           77 -> receive Display data
//           80 -> enable/disable metronome blinking
//           81 -> enable session box
//           82 -> receive Display text
//           99 -> raw RGB Data

void send_sysex(byte _size, byte *data) {
  Serial1.write(240);
  for (byte i; i < _size; i++) {
    Serial1.write(data[i]);
  }
  Serial1.write(247);
}
void onSysEx(const uint8_t *data) { //, unsigned _length, bool complete) {
  
  if (data[1] == 122 && data[2] == 29 && data[3] == 1 && data[4] == 19) {
    switch (data[5]) {
      case 68: {    // Handshake with Editor
          byte sysexArrayBoot[] = {240, 122, 29, 1, 19, 68, 1, 0, 247};  //String that answers to the MIDI Remote Script for Ableton Live
          MIDI.sendSysEx(9, sysexArrayBoot, true);
          send_sysex(9, sysexArrayBoot);
        }
        break;

      case 69: {    // Handshake with Live
          byte sysexArrayBoot[] = {240, 122, 29, 1, 19, 73, 1, 0, 33, 1, 127, 0, 127, 247};  //String that answers to the MIDI Remote Script for Ableton Live
          MIDI.sendSysEx(14, sysexArrayBoot, true);
          send_sysex(14, sysexArrayBoot);
          check_layout_led();
          for (byte i = 0; i < 2; i++) {
            if (EEPROM.read(300 + i) != 255) {
              byte sysex_array[8] = {240, 122, 29, 1, 19, 80 + i, EEPROM.read(300 + i), 247};
            }
          }
        }
        break;

      case 70: {    // Short Buttons data received
          byte rcvd_layout = data[6];
          byte num = data[7];
          byte btn_ctrl = data[8];
          byte btn_type = data[9];
          byte btn_chnl = data[10];
          b[num].short_type[rcvd_layout] = btn_type;
          b[num].short_control[rcvd_layout] = btn_ctrl;
          b[num].short_ch[rcvd_layout] = btn_chnl;

          eeprom_store(rcvd_layout, num, btn_type, btn_ctrl, btn_chnl);
          if (btn_type == 1)
          { byte acknowledgment_array[7] = {240, 122, 29, 1, 19, 78, 247};
            MIDI.sendSysEx(7, acknowledgment_array, true);
          }
        }
        break;

      case 71:  {    // Long Buttons data received
          byte rcvd_layout = data[6];
          byte num = data[7];
          byte btn_ctrl = data[8];
          byte btn_type = data[9];
          byte btn_chnl = data[10];
          b[num].long_type[rcvd_layout] = btn_type;
          b[num].long_control[rcvd_layout] = btn_ctrl;
          b[num].long_ch[rcvd_layout] = btn_chnl;
          eeprom_store(rcvd_layout, num + 6, btn_type, btn_ctrl, btn_chnl);
          if (btn_type == 1)
          { byte acknowledgment_array[7] = {240, 122, 29, 1, 19, 78, 247};
            MIDI.sendSysEx(7, acknowledgment_array, true);
          }
        }
        break;
      case 72: {    // LEDs data received
          byte rcvd_layout = data[6];
          byte num = data[7];
          byte led_ctrl = data[8];
          byte led_chnl = data[10];
          l[num].control[rcvd_layout] = led_ctrl;
          l[num].state = led_chnl;
          eeprom_store(rcvd_layout, num + 12, 1, led_ctrl, led_chnl);
          // if (btn_type==1)
          { byte acknowledgment_array[7] = {240, 122, 29, 1, 19, 78, 247};
            MIDI.sendSysEx(7, acknowledgment_array, true);
          }
        }
        break;

      case 73: {    // Analog data received
          byte rcvd_layout = data[6];
          byte num = data[7];
          byte control = data[8];
          byte channel = data[10];
          a[num].control[rcvd_layout] = control;
          a[num].channel[rcvd_layout] = channel;
          eeprom_store(rcvd_layout, num + 18, 1, control, channel);
          // if (btn_type==1)
          { byte acknowledgment_array[7] = {240, 122, 29, 1, 19, 78, 247};
            MIDI.sendSysEx(7, acknowledgment_array, true);
          }
        }
        break;

      case 74: { // Receiving {240, 122, 29, 1, 19, 74} sends each control 1 by 1 {240, 122, 29, 1, 19, 77, Layout, Control, CC Number, Channel, Type, 247}
          byte sysex_to_send[12] = {240, 122, 29, 1, 19, 74, 0, 0, 0, 0, 0, 247};
          for ( byte layout_number = 0; layout_number < 3; layout_number ++) {
            sysex_to_send[6] = layout_number;
            for ( byte i = 0; i < NUM_BUTTONS; i += 1) {
              sysex_to_send[7]  = i;
              sysex_to_send[8]  = b[i].short_control[layout_number];
              sysex_to_send[9] = b[i].short_ch[layout_number];
              sysex_to_send[10] = b[i].short_type[layout_number];
              MIDI.sendSysEx(12, sysex_to_send, true);
              delay(2);
            }
            for ( byte i = 0; i < NUM_BUTTONS; i += 1) {
              sysex_to_send[7]  = i + 6;
              sysex_to_send[8]  = b[i].long_control[layout_number];
              sysex_to_send[9] = b[i].long_ch[layout_number];
              sysex_to_send[10] = b[i].long_type[layout_number];
              MIDI.sendSysEx(12, sysex_to_send, true);
              delay(2);
            }
            for ( byte i = 0; i < NUM_LEDS; i += 1) {
              sysex_to_send[7]  = i + 12;
              sysex_to_send[8]  = l[i].control[layout_number];
              sysex_to_send[9] = l[i].state;
              sysex_to_send[10] = 1;
              MIDI.sendSysEx(12, sysex_to_send, true);
              delay(2);
            }
            for ( byte i = 0; i < NUM_POTS; i += 1) {
              sysex_to_send[7]  = i + 18;
              sysex_to_send[8]  = a[i].control[layout_number];
              sysex_to_send[9] = a[i].channel[layout_number];
              MIDI.sendSysEx(12, sysex_to_send, true);
              delay(2);
            }

            sysex_to_send[7]  = 22;
            sysex_to_send[8]  = disp.layout[layout_number];
            sysex_to_send[9] = 1;
            sysex_to_send[10] = 1;
            MIDI.sendSysEx(12, sysex_to_send, true);
            delay(2);
          }
          byte end_array[7] = {240, 122, 29, 1, 19, 79, 247};
          MIDI.sendSysEx(7, end_array, true);
        }
        break;

      case 75: {   // Layout Data received
          clear_leds();
          current_layout = data[6];
          check_layout_led();
        }
        break;

      case 76: {   // Disconnect message received
          for (byte i = 0; i < 32 ; i++) {
            disp.text[i] = 15;
          }
          disp.build_text(10);
          clear_leds();
        }
        break;

      case 77: {    // Display data received
          byte rcvd_layout = data[6];
          byte layout = data[8];
          disp.layout[rcvd_layout] = layout;
          eeprom_store(rcvd_layout, 22, 0, layout, 0);
        }
        break;

      case 80: {
          EEPROM.write(220 + data[5], data[6]); //writes EEPROM #300 (tempo)
          MIDI.sendSysEx(8, data, true);
          send_sysex(8, data);
        }
        break;

      case 81: {
          EEPROM.write(220 + data[5], data[6]); //writes EEPROM #301 (session box)$
          MIDI.sendSysEx(8, data, true);
          send_sysex(8, data);
        }
        break;

      case 82: {   // text received
          if (data[6] == disp.layout[current_layout]) {
            // disp.clear_text();
            for (byte i = 0; i < data[7] ; i++) {
              disp.text[i] =  data[8 + i];
            }
            disp.build_text(data[7]);
          }
        }
        break;

      case 83: {   // Receive Looper number from Live
          byte btn_num = data[8];
          byte btn_type = data[9];
          byte btn_chnl = data[10];

          for (byte i = 0; i < NUM_LAYOUT; i++) {
            for (byte j = 0; j < NUM_BUTTONS; j++) {
              if (b[j].short_ch[i] == btn_chnl && b[j].short_type[i] == 0) {
                b[j].short_type[i] = btn_type;
                b[j].short_control[i] = btn_num;
                b[j].short_ch[i] = btn_chnl;
                eeprom_store(i, j, btn_type, btn_num, btn_chnl);
              }
              if (b[j].long_ch[i] == btn_chnl && b[j].long_type[i] == 0) {
                b[j].long_type[i] = btn_type;
                b[j].long_control[i] = btn_num;
                b[j].long_ch[i] = btn_chnl;
                eeprom_store(i, j + 6, btn_type, btn_num, btn_chnl);
              }

            }
          }
        }

        break;

    }
  }
}

void eeprom_store(byte rcvd_layout, byte  num, byte  type, byte  control, byte  channel) {
  EEPROM.write(100 * rcvd_layout + num, type);
  EEPROM.write(100 * rcvd_layout + num + 30, control);
  EEPROM.write(100 * rcvd_layout + num + 60, channel);
}

void onControlChange(byte channel, byte control, byte value) {
  check_led(channel, control, value);
}

void check_led(byte channel, byte control, byte value) {
  for (int i = 0; i < NUM_LEDS; i++) {
    if (l[i].control[current_layout] == control) {
      l[i].set_color(value, channel);
      l[i].led_update(b[i].held);
    }
  }
}

void check_layout_led() {
  byte color = 15; //14;
  if (current_layout == 1) color = 21;
  else if (current_layout == 2) color = 9;
  check_led(16, 50, color);
}


byte external_MIDI_control[NUM_BUTTONS];
byte external_MIDI_channel[NUM_BUTTONS];

void on_MIDI_ControlChange(byte channel, byte control, byte value) {
  if (!MIDI_Mode) check_led(channel, control, value);
  else {
    for (byte i = 0; i < NUM_BUTTONS; i++) {
      if (channel == external_MIDI_channel[i] && control == external_MIDI_control[i]) {
        if (value > 0) b[i].set_button_on();
        else b[i].set_button_off();
      }
    }
  }
}

void sendMessage(byte type, byte control, byte channel) {
  switch (type) {
    case 0:
      sendNote(control, 127, channel);
      sendNote(control, 0, channel);
      break;
    case 1:
      sendCC(control, 127, channel);
      sendCC(control, 0, channel);
      break;
    case 2:
      sendPC(control, channel);
      break;
  }
}

void sendCC (byte control, byte value, byte channel) {
  // MIDI_DIN.sendControlChange(control, value, channel);
  MIDI.sendControlChange(control, value, channel);
  
    Serial1.write(channel+175);
    Serial1.write(control);
    Serial1.write(value);
}

void sendNote (byte control, byte value, byte channel) {
  // MIDI_DIN.sendNoteOn(control, value, channel);
  MIDI.sendNoteOn(control, value, channel);
}

void sendPC (byte program, byte channel) {
  // MIDI_DIN.sendProgramChange(program, channel);
  MIDI.sendProgramChange(program, channel);
}
