#include <stdio.h>
#include "pico/stdlib.h"
#include "limit_switches.h"
#include "led.h"


int main()
{
    stdio_init_all();

    // Initialise limit switches
    initialise_limit_switches();

    // Initialise the LED outputs
    int spindleMotorPin = initialise_led(0);

    while (true)
    {
        if (monitor_limit_switches() == 1)
        {
            set_led(spindleMotorPin, 1);
        }
        else
        {
            set_led(spindleMotorPin, 0);
        }
    }
}