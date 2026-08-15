#include <stdbool.h>
#include "x_axis.h"


#define SEQUENCE_LENGTH 10


int main() {
    char sequence[SEQUENCE_LENGTH + 1] = "Xnnnnnnnnn";
    char current_step;

    while (true) {
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


    return 0;
}