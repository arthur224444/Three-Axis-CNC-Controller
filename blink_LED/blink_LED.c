#include <stdio.h>
#include "pico/stdlib.h"
#include "limit_switches.h"
#include "pin.h"
#include "axis.h"
#include "x_axis.h"


int main()
{
    stdio_init_all();

    // Initialise limit switches
    initialise_limit_switches();

    // Initialise the LED outputs
    int spindleMotorPin = initialise_pin(0);
    
    int xAxisPulsePin = initialise_pin(7);
    int xAxisDirPin = initialise_pin(8);
    int xAxisEnablePin = initialise_pin(9);

    int yAxisPulsePin = initialise_pin(10);
    int yAxisDirPin = initialise_pin(11);
    int yAxisEnablePin = initialise_pin(12);

    int zAxisPulsePin = initialise_pin(13);
    int zAxisDirPin = initialise_pin(14);
    int zAxisEnablePin = initialise_pin(15);

    while (true)
    {
        if (monitor_limit_switches() == 1)
        {
            set_pin(spindleMotorPin, 0);
            set_pin(xAxisPulsePin, 0);
            set_pin(xAxisDirPin, 0);
            set_pin(xAxisEnablePin, 0);
            set_pin(yAxisPulsePin, 0);
            set_pin(yAxisDirPin, 0);
            set_pin(yAxisEnablePin, 0);
            set_pin(zAxisPulsePin, 0);
            set_pin(zAxisDirPin, 0);
            set_pin(zAxisEnablePin, 0);
        }
        else
        {
            set_pin(spindleMotorPin, 1);
            set_pin(xAxisPulsePin, 1);
            set_pin(xAxisDirPin, 1);
            set_pin(xAxisEnablePin, 1);
            set_pin(yAxisPulsePin, 1);
            set_pin(yAxisDirPin, 1);
            set_pin(yAxisEnablePin, 1);
            set_pin(zAxisPulsePin, 1);
            set_pin(zAxisDirPin, 1);
            set_pin(zAxisEnablePin, 1);
        }
    }
}