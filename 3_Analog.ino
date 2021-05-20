//////////////////////////////
// ANALOG
//////////////////////////////

class AnalogPot {

  private:
    ResponsiveAnalogRead analog_read;
    int pin;
    int num;
  public:
    AnalogPot(int num) : analog_read(a_pins[num], true) {pin = a_pins[num];}
    byte control[NUM_LAYOUT] = {num, num, num};
    byte channel[NUM_LAYOUT] = {16, 16, 16};
    byte valuePot;
    byte lastValuePot;
    void check_pot() {
      analog_read.update();
      valuePot = map( analog_read.getValue(), 0, 1024, 0, 128);
      valuePot = constrain( valuePot, 0, 127);

      if ((valuePot != lastValuePot)) {
        lastValuePot = valuePot;
        if (b[5].held == HIGH) {
          if (pin == a_pins[1] || pin == a_pins[3]) {
            BRIGHTNESS = map( analog_read.getValue(), 0, 1024, 30, 255);
            FastLED.setBrightness(BRIGHTNESS);
            FastLED.show();
            EEPROM.write(298, BRIGHTNESS);

          }
          if (pin == a_pins[0] || pin == a_pins[2]) {
            matrix_brightness =  map(analog_read.getValue(), 0, 1024, 30, 0);
            EEPROM.write(299, matrix_brightness);
          }
        }
        else sendCC(control[current_layout], valuePot, channel[current_layout]);
      }
    }
};

AnalogPot a[NUM_POTS] = {AnalogPot(0), AnalogPot(1)}; 
