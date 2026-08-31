#include "emergency_stop.h"
#include <stdio.h>
#include "spindle.h"

static volatile int machine_emergency_stopped = 0;

void emergency_stop() {
    machine_emergency_stopped = 1;
    spindle_on_off(0);  // Turns the spindle motor off
}

void reset_emergency_stop() {
    machine_emergency_stopped = 0;
}

int check_emergency_stop() {
    return machine_emergency_stopped;
}