#include <stdio.h>

static volatile int machine_emergency_stopped = 0;

void emergency_stop() {
    machine_emergency_stopped = 1;
}

void reset_emergency_stop() {
    machine_emergency_stopped = 0;
}

int check_emergency_stop() {
    return machine_emergency_stopped;
}