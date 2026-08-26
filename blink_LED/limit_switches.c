#include "pin.h"
#include "pico/stdlib.h"


static const int X_MIN_GPIO_PIN = 1;
static const int X_MAX_GPIO_PIN = 2;
static const int Y_MIN_GPIO_PIN = 3;
static const int Y_MAX_GPIO_PIN = 4;
static const int Z_MIN_GPIO_PIN = 5;
static const int Z_MAX_GPIO_PIN = 6;

static void initialise_limit_switch_pins() {
    initialise_input_pin(X_MIN_GPIO_PIN);
    initialise_input_pin(X_MAX_GPIO_PIN);
    initialise_input_pin(Y_MIN_GPIO_PIN);
    initialise_input_pin(Y_MAX_GPIO_PIN);
    initialise_input_pin(Z_MIN_GPIO_PIN);
    initialise_input_pin(Z_MAX_GPIO_PIN);
}

int check_limit_switches() {
    static int pins_initialised = 0;

    if (pins_initialised == 0) {
        initialise_limit_switch_pins();
        pins_initialised = 1;
    }

    int switch_pressed = 0;

    // Check the limit switches
    if ((gpio_get(X_MIN_GPIO_PIN) == 0) || 
        (gpio_get(X_MAX_GPIO_PIN) == 0) || 
        (gpio_get(Y_MIN_GPIO_PIN) == 0) || 
        (gpio_get(Y_MAX_GPIO_PIN) == 0) || 
        (gpio_get(Z_MIN_GPIO_PIN) == 0) || 
        (gpio_get(Z_MAX_GPIO_PIN) == 0)
    )
    {
        switch_pressed = 1;
    }

    return switch_pressed;
}
