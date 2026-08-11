#include <stdio.h>
#include "pico/stdlib.h"
#include "limit_switches.h"

int main()
{
    stdio_init_all();

    // Initialise limit switches
    initialise_limit_switches();

    // Initialise the LED output (GP16)
    int LEDPin = 16;
    gpio_init(LEDPin);
    gpio_set_dir(LEDPin, GPIO_OUT);

    while (true)
    {
        if (monitor_limit_switches() == 1)
        {
            gpio_put(LEDPin, 1);
        }
        else
        {
            gpio_put(LEDPin, 0);
        }
    }
}