#include <stdbool.h>
#include <stdio.h>
#include "x_axis.h"
#include "pico/stdlib.h"
#include "emergency_stop.h"


#define SEQUENCE_LENGTH 10


int main() {
    stdio_init_all();

    printf("Here");

    char sequence[SEQUENCE_LENGTH + 1] = "Xxnnnnnnnn";
    char current_step;

    printf("Here2");

    while (true) {

        sleep_ms(1000);

        if (check_emergency_stop() == 0) {

            for (int i = 0; i < SEQUENCE_LENGTH; i++) {
                current_step = sequence[i];

                if (current_step == 'X') {
                    step_x(1);

                }
                else if (current_step == 'x') {
                    step_x(-1);

                }
                else if (current_step == 'Y') {

                }
                else if (current_step == 'y') {

                }
                else if (current_step == 'Z') {

                }
                else if (current_step == 'z') {

                }
                else {

                }

            }

        }
        else {
            printf("Emergency stop has stopped the step from being made\n");
        }
    }


    return 0;
}