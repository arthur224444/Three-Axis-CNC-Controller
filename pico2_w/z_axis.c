#include "z_axis.h"
#include "axis.h"


static const AxisInfo axis_info = {
    .pul_pin = 13,
    .dir_pin = 14,
    .ena_pin = 15,
    .axis_label = 'Z'
};


int step_z(int direction, int force_step) {
    // Move motor in the X axis

    static int pins_initialised = 0;
    static int position = 0;
    int success;

    // Make the step
    StepReturnData step_data = step(axis_info, pins_initialised, position, direction, force_step);
    pins_initialised = step_data.pins_initialised;
    position = step_data.position;
    success = step_data.success;
 
    return success;
}
