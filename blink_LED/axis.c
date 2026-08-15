#include <stdio.h>
#include "axis.h"
#include "limit_switches.h"
#include "pico/stdlib.h"
#include "pin.h"
// Maybe limit_switches should be multiple switches but I'm not sure

// What is this file going to do?:
// - Monitor for the limit switches being reached (both of them)
// - Control the pulse, dir and enabel pins based on an input to move the motor by a step
// - Return the actual_position of the axis after hte move has been done 
//    - This needs to take into account hitting the limit switches (that sets it and probably raises a warning)
//    - And this also needs to count motor steps that it's asking the motor to make

int ENA_SETTLE_TIME_MS = 250;
int PUL_TIME_MS = 1;
int DIR_TIME_MS  = 5;

void initialise_axis_pins(int stepper_pul_pin, int stepper_dir_pin, int stepper_ena_pin, int limit_switch_max_pin, int limit_switch_min_pin) {
    initialise_pin(stepper_pul_pin);
    initialise_pin(stepper_dir_pin);
    initialise_pin(stepper_ena_pin);
    initialise_pin(limit_switch_max_pin);
    initialise_pin(limit_switch_min_pin);
}

int check_limit_switches(max_limit_switch_pin, max_limit_switch_position, min_limit_switch_pin, min_limit_switch_position, expected_position) {
    // Returns the position of the axis based on the limit switch if either limit switch is pressed, else returns the axis position it's provided with
    // Note, returning the expected position does not prove that the axis is actually in the expected position, it just means that neither limit switch 
    // was reached and therefore it might be in the right place but if it isn't the limit switches wouldn't be able to tell.

    // Check the limit switches
    if (gpio_get(max_limit_switch_pin) == 0)
    {
        return max_limit_switch_position;
    }
    else if (gpio_get(min_limit_switch_pin) == 0) {
        return min_limit_switch_position;
    }
    else {
        return expected_position;
    }
}


StepReturnData step(AxisInfo axis_info, int pins_initialised, int position, int direction) {
    int skip = 0;

    // Initialise the pins if they're not already initialised
    if (pins_initialised == 0) {
        initialise_axis_pins(axis_info.pul_pin, axis_info.dir_pin, axis_info.ena_pin, axis_info.max_limit_switch_pin, axis_info.min_limit_switch_pin);
        pins_initialised = 1;
    }

    // Check the limit switches
    int position_check = check_limit_switches(axis_info.max_limit_switch_pin, axis_info.max_limit_switch_position, axis_info.min_limit_switch_pin, axis_info.min_limit_switch_position, position);
    if (position_check != position) {
        printf("Error: Expected actual_position %d and actual actual_position %d do not match!\n", position, position_check);
        position = position_check;
        skip = 1;
    }

    // Check the step isn't going to exceeed the max or min positions for the axis
    if ((direction == 1 && position == axis_info.max_limit_switch_position) || (direction == -1 && position == axis_info.min_limit_switch_position)) {
        skip = 1;
        printf("Error: Making this step would crash the machine into an end of the %s axis.\n", axis_info.axis_label);
    }

    if (skip == 0) {
        // Enable the motor
        set_pin(axis_info.ena_pin, 0);
        sleep_ms(ENA_SETTLE_TIME_MS);

        // Set direction
        if (direction == 1) {
            set_pin(axis_info.dir_pin, 1);
        }
        else {
            set_pin(axis_info.dir_pin, 0);
        }
        sleep_ms(DIR_TIME_MS);

        // Step the motor
        set_pin(axis_info.dir_pin, 1);
        sleep_ms(PUL_TIME_MS);
        set_pin(axis_info.pul_pin, 0);

        // Disable the motor
        set_pin(axis_info.ena_pin, 1);
        sleep_ms(ENA_SETTLE_TIME_MS);

        // Update position 
        if (direction == 1) {position++;}
        else {position--;}
    }

    else {
        printf("Step skipped due to errors.\n\n");
    }

    // Assemble return data
    StepReturnData data;
    data.pins_initialised = pins_initialised;
    data.position = position;

    return data;
}

