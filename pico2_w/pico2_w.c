#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "hardware/spi.h"
#include "pico/stdlib.h"
#include "pico/multicore.h"

#include "x_axis.h"
#include "y_axis.h"
#include "z_axis.h"
#include "emergency_stop.h"
#include "limit_switches.h"


#define SEQUENCE_LENGTH 10
uint8_t received_data[10];  // A little box in memory for holding 10 bytes received over SPI


int main() {
    stdio_init_all();

    gpio_set_function(18, GPIO_FUNC_SPI);
    gpio_set_function(19, GPIO_FUNC_SPI);
    gpio_set_function(20, GPIO_FUNC_SPI);
    gpio_set_function(21, GPIO_FUNC_SPI);

    spi_init(spi0, 0);
    spi_set_slave(spi0, true);

    while (true) {
        // SPI code
        spi_read_blocking(spi0, 0, received_data, 10);

        printf("%.*s\n", 10, received_data);
    }

    /*
    stdio_init_all();

    multicore_launch_core1(monitor_limit_switches);

    char sequence[SEQUENCE_LENGTH + 1];
    int sequence_len;
    char current_step;

    while (true) {
        strcpy(sequence, "XxYyZznnnn");
        sequence_len = strlen(sequence);

        sleep_ms(1000);

        for (int i = 0; i < SEQUENCE_LENGTH; i++) {

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
    */


    return 0;
}