#include <stdio.h>
#include "pico/stdlib.h"
#include "limit_switches.h"
#include "led.h"


int main()
{
    stdio_init_all();

    // Initialise limit switches
    initialise_limit_switches();

    // Initialise the LED output (GP16)
    initialise_led();

    while (true)
    {
        if (monitor_limit_switches() == 1)
        {
            set_led(1);
        }
        else
        {
            set_led(0);
        }
    }
}