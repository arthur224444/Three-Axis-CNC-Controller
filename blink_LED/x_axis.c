#include "x_axis.h"
#include "axis.h"


static const AxisInfo axis_info = {
    .pul_pin = 7,
    .dir_pin = 8,
    .ena_pin = 9,
    .axis_label = 'X'
};


int step_x(int direction) {
    // Move motor in the X axis

    static int pins_initialised = 0;
    static int position = 0;

    // Make the step
    StepReturnData step_data = step(axis_info, pins_initialised, position, direction);
    pins_initialised = step_data.pins_initialised;
    position = step_data.position;
 
    return position;
}

