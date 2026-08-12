#include "pico/stdlib.h"
#include "led.h"

// The LED must be connected to pin 16 on the Pi Pico 2W

int LEDPin = 16;

void initialise_led(void) {
    gpio_init(LEDPin);
    gpio_set_dir(LEDPin, GPIO_OUT);
}

void set_led(int on) {
    if (on == 1) {
        gpio_put(LEDPin, 1);
    }
    else
    {
        gpio_put(LEDPin, 0);
    }
}
