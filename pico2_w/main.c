#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "hardware/spi.h"
#include "pico/stdlib.h"
#include "pico/stdio_usb.h"
#include "pico/multicore.h"

#include "x_axis.h"
#include "y_axis.h"
#include "z_axis.h"
#include "emergency_stop.h"
#include "limit_switches.h"
#include "spindle.h"


#define SEQUENCE_LENGTH 10
uint8_t sequence[SEQUENCE_LENGTH];  // A little box in memory for holding 10 bytes received over SPI


int main() {
    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(10);
    }

    multicore_launch_core1(monitor_limit_switches);

    char current_step;

    while (true) {

        for (int i = 0; i < SEQUENCE_LENGTH; i++) {
            sequence[i] = (uint8_t)getchar();
        }

        char success = '1';
        int step_success = 1;

        for (int i = 0; i < SEQUENCE_LENGTH; i++) {

            if (check_emergency_stop() == 1) {
                spindle_on_off(0);

            }

            current_step = sequence[i];

            if (current_step == 'X') {
                step_success = step_x(1, 0);

            }
            else if (current_step == 'x') {
                step_success = step_x(-1, 0);

            }
            else if (current_step == 'Y') {
                step_success = step_y(1, 0);

            }
            else if (current_step == 'y') {
                step_success = step_y(-1, 0);

            }
            else if (current_step == 'Z') {
                step_success = step_z(1, 0);

            }
            else if (current_step == 'z') {
                step_success = step_z(-1, 0);

            }

            // Force steps, ignoring emergency_stop
            else if (current_step == 'A') {
                step_success = step_x(1, 1);
            
            }
            else if (current_step == 'a') {
                step_success = step_x(-1, 1);
            
            }
            else if (current_step == 'B') {
                step_success = step_y(1, 1);
            
            }
            else if (current_step == 'b') {
                step_success = step_y(-1, 1);
            
            }
            else if (current_step == 'C') {
                step_success = step_z(1, 1);
            
            }
            else if (current_step == 'c') {
                step_success = step_z(-1, 1);
            
            }

            // Handle padding characters
            else if (current_step == 'n') {
                // Do nothing
            }

            // Spindle on/off
            else if (current_step == 'S') {
                if (check_emergency_stop() == 0) {
                    spindle_on_off(1);
                }

            }
            else if (current_step == 's') {
                spindle_on_off(0);

            }

            // Reset emergency stop
            else if (current_step == 'R') {
                reset_emergency_stop();

            }

            
            else {
                spindle_on_off(0);

                success = '0';
            }

            if (step_success == 0) {
                success = '0';
            }
        }

        putchar(success);
        fflush(stdout);

    }

    return 0;
}