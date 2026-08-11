#include "pico/stdlib.h"
#include "limit_switches.h"

int LimitSwitches[6] = {
    X_MAX,
    X_MIN,
    Y_MAX,
    Y_MIN,
    Z_MAX,
    Z_MIN
};

// Initialise limit switches
void initialise_limit_switches(void)
{
    for (int i = 0; i < sizeof(LimitSwitches) / sizeof(LimitSwitches[0]); i++)
    {
        gpio_init(LimitSwitches[i]);
        gpio_set_dir(LimitSwitches[i], GPIO_IN);
        gpio_pull_up(LimitSwitches[i]);
    }
}

// Check whether any limit switch is pressed
int monitor_limit_switches(void)
{
    for (int i = 0; i < sizeof(LimitSwitches) / sizeof(LimitSwitches[0]); i++)
    {
        if (gpio_get(LimitSwitches[i]) == 0)
        {
            return 1;
        }
    }

    return 0;
}