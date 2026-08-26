#include <stdbool.h>
#include <stdio.h>
#include "x_axis.h"
#include "y_axis.h"
#include "z_axis.h"
#include "pico/stdlib.h"
#include "emergency_stop.h"
#include "limit_switches.h"



#define SEQUENCE_LENGTH 10


int main() {
    stdio_init_all();

    char sequence[SEQUENCE_LENGTH + 1] = "XxYyZznnnn";
    char current_step;
    int limit_switch_reached = 0;

    while (true) {

        sleep_ms(1000);

        for (int i = 0; i < SEQUENCE_LENGTH; i++) {

            limit_switch_reached = check_limit_switches();
            if (limit_switch_reached == 1) {
                emergency_stop();
            }

            if (check_emergency_stop() == 0) {

            
                current_step = sequence[i];

                if (current_step == 'X') {
                    step_x(1);

                }
                else if (current_step == 'x') {
                    step_x(-1);

                }
                else if (current_step == 'Y') {
                    step_y(1);

                }
                else if (current_step == 'y') {
                    step_y(-1);

                }
                else if (current_step == 'Z') {
                    step_z(1);

                }
                else if (current_step == 'z') {
                    step_z(-1);

                }
                else {

                }
            }

            else {
                printf("Emergency stop has stopped the step from being made\n");
            }

        }
    }


    return 0;
}