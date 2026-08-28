#include <stdio.h>
#include "axis.h"
#include "pico/stdlib.h"
#include "pin.h"
#include "emergency_stop.h"

// What is this file going to do?:
// - Monitor for the limit switches being reached (both of them)
// - Control the pulse, dir and enabel pins based on an input to move the motor by a step
// - Return the actual_position of the axis after hte move has been done 
//    - This needs to take into account hitting the limit switches (that sets it and probably raises a warning)
//    - And this also needs to count motor steps that it's asking the motor to make

int ENA_SETTLE_TIME_MS = 250;
int PUL_TIME_MS = 1;
int DIR_TIME_MS  = 5;

void initialise_axis_pins(int stepper_pul_pin, int stepper_dir_pin, int stepper_ena_pin) {
    initialise_output_pin(stepper_pul_pin);
    initialise_output_pin(stepper_dir_pin);
    initialise_output_pin(stepper_ena_pin);
}


StepReturnData step(AxisInfo axis_info, int pins_initialised, int position, int direction) {
    int skip = 0;

    // Initialise the pins if they're not already initialised
    if (pins_initialised == 0) {
        initialise_axis_pins(axis_info.pul_pin, axis_info.dir_pin, axis_info.ena_pin);
        pins_initialised = 1;
    }

    if (check_emergency_stop() == 0) {

        // Check the step isn't going to exceeed the max or min positions for the axis
        // TODO Implement this, setting skip to 1 if it would exceed the axis

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
            if (check_emergency_stop() == 0) {  // Check for emergency stop in case it's been triggered since the last check
                set_pin(axis_info.pul_pin, 1);
                sleep_ms(PUL_TIME_MS);
                set_pin(axis_info.pul_pin, 0);

                // Update position 
                if (direction == 1) {position++;}
                else {position--;}
            }

            // Disable the motor
            set_pin(axis_info.ena_pin, 1);
            sleep_ms(ENA_SETTLE_TIME_MS);
        }

        else {
            printf("Step skipped due to errors.\n\n");
        }
    
    }

    else {
        printf("Emergency stop reached so step was skipped\n");
    }

    // Assemble return data
    StepReturnData data;
    data.pins_initialised = pins_initialised;
    data.position = position;

    return data;
}

