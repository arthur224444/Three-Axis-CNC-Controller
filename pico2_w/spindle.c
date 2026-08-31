#include "pico/stdlib.h"
#include "pin.h"


SPINDLE_ENABLE_PIN = 0;


static void initialise_pins(int spindle_enable_pin) {
    initialise_output_pin(spindle_enable_pin);
}


int spindle_on_off(int enable) {
    static int pins_initialised = 0;
    if (pins_initialised == 0) {
        initialise_pins(SPINDLE_ENABLE_PIN);
        pins_initialised = 1;
    }

    set_pin(SPINDLE_ENABLE_PIN, enable);
    return 1;
}
