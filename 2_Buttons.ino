//////////////////////////////
// BUTTONS
//////////////////////////////

class Button {
  private:
    byte num = 0;
    unsigned long time_pressed = 0;
    Bounce bouncer = Bounce( 0, 25 );
  public:
    Button(byte pin, byte number) {
      num = number;
      bouncer = Bounce( pin, 25 );
      pinMode(pin, INPUT_PULLUP);
    };

    byte short_control[NUM_LAYOUT] = {21, 2, 3};
    byte long_control[NUM_LAYOUT] = {31, 4, 5};
    byte short_ch[NUM_LAYOUT] = {16, 16, 16};
    byte long_ch[NUM_LAYOUT] = {16, 16, 16};
    byte short_type[NUM_LAYOUT] = {1, 1, 1};
    byte long_type[NUM_LAYOUT] = {1, 1, 1};
    bool state = LOW;
    bool held = LOW;
    bool latch = LOW;

    void update_button() {
      bouncer.update();
      state = !bouncer.read();
      check_button();
    }

    void check_button() {
      if (state && !held && !latch) {
        time_pressed = millis();
        held = HIGH;
        l[num].led_update(HIGH);
      }
      if (held && !state) {
        l[num].led_update(LOW);
        if (!latch) {
          sendMessage(short_type[current_layout], short_control[current_layout], short_ch[current_layout]);
        }
        held = LOW;
        latch = LOW;
      }
      if (held && ((millis() - time_pressed) > 1000) && !latch) {
        l[num].led_update(LOW);
        sendMessage(long_type[current_layout], long_control[current_layout], long_ch[current_layout]);
        latch = HIGH;
      }
    }
    void set_button_on() {
      state = HIGH;
    }
    void set_button_off() {
      state = LOW;
    }
};

Button b[NUM_BUTTONS] = {Button(b_pins[0], 0), Button(b_pins[1], 1), Button(b_pins[2], 2), Button(b_pins[3], 3), Button(b_pins[4], 4), Button(b_pins[5], 5)};
