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
    int xAxisStepPin = initialise_led(7);
    int yAxisStepPin = initialise_led(8);
    int zAxisStepPin = initialise_led(9);

    while (true)
    {
        if (monitor_limit_switches() == 1)
        {
            set_led(spindleMotorPin, 0);
            set_led(xAxisStepPin, 0);
            set_led(yAxisStepPin, 0);
            set_led(zAxisStepPin, 0);
        }
        else
        {
            set_led(spindleMotorPin, 1);
            set_led(xAxisStepPin, 1);
            set_led(yAxisStepPin, 1);
            set_led(zAxisStepPin, 1);
        }
    }
}