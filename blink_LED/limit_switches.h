#ifndef LIMIT_SWITCHES_H
#define LIMIT_SWITCHES_H

typedef enum
{
    X_MAX = 1,
    X_MIN = 2,
    Y_MAX = 3,
    Y_MIN = 4,
    Z_MAX = 5,
    Z_MIN = 6
} LimitSwitchGPIOS;

void initialise_limit_switches(void);
int monitor_limit_switches(void);

#endif