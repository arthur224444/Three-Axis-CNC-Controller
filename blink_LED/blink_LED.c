#include <stdio.h>
#include "pico/stdlib.h"

int main()
{
    stdio_init_all();

    typedef enum
    {
        X_MAX = 1,
        X_MIN = 2,
        Y_MAX = 3,
        Y_MIN = 4,
        Z_MAX = 5,
        Z_MIN = 6
    } LimitSwitchGPIOS;

    int LimitSwitches[6] = {
        X_MAX,
        X_MIN,
        Y_MAX,
        Y_MIN,
        Z_MAX,
        Z_MIN
    };

    int SwitchLEDOn = 0;

    // Initialise limit switches
    for (int i = 0; i < sizeof(LimitSwitches) / sizeof(LimitSwitches[0]); i++) {
        gpio_init(LimitSwitches[i]);
        gpio_set_dir(LimitSwitches[i], GPIO_IN);
        gpio_pull_up(LimitSwitches[i]);
    }

    // Initialise the LED output (GP16)
    int LEDPin = 16;
    gpio_init(LEDPin);
    gpio_set_dir(LEDPin, GPIO_OUT);

    while (true)
    {
        // Check for each switch whether that switch is pressed, and if so, put the LED on
        SwitchLEDOn = 0;
        for (int i = 0; i < sizeof(LimitSwitches) / sizeof(LimitSwitches[0]); i++) {
            if (gpio_get(LimitSwitches[i]) == 0)
            {
                SwitchLEDOn = 1;
                continue;
            }
        }

        if (SwitchLEDOn == 1) {
            gpio_put(LEDPin, 1);
        }
        else
        {
            gpio_put(LEDPin, 0);
        }
    }
}