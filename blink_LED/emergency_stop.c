#include <stdio.h>

static int machine_emergency_stopped = 0;

void emergency_stop() {
    machine_emergency_stopped = 1;
    printf("The machine has been emergency stopped\n");
}

void reset_emergency_stop() {
    printf("Resetting emergency stop, enabling machine to operate again\n");
    machine_emergency_stopped = 0;
}

int check_emergency_stop() {
    return machine_emergency_stopped;
}