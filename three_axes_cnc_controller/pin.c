#include "pico/stdlib.h"
#include "pin.h"

// The LED must be connected to pin 16 on the Pi Pico 2W

int initialise_output_pin(int GPIOPin) {
    gpio_init(GPIOPin);
    gpio_set_dir(GPIOPin, GPIO_OUT);
    return GPIOPin;
}

int initialise_input_pin(int GPIOPin) {
    gpio_init(GPIOPin);
    gpio_set_dir(GPIOPin, GPIO_IN);
    gpio_pull_up(GPIOPin);
    return GPIOPin;
}

void set_pin(int GPIOPin, int on) {
    if (on == 1) {
        gpio_put(GPIOPin, 1);
    }
    else
    {
        gpio_put(GPIOPin, 0);
    }
}
