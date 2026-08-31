#include "y_axis.h"
#include "axis.h"


static const AxisInfo axis_info = {
    .pul_pin = 10,
    .dir_pin = 11,
    .ena_pin = 12,
    .axis_label = 'Y'
};


int step_y(int direction, int force_step) {
    // Move motor in the X axis

    static int pins_initialised = 0;
    static int position = 0;

    // Make the step
    StepReturnData step_data = step(axis_info, pins_initialised, position, direction, force_step);
    pins_initialised = step_data.pins_initialised;
    position = step_data.position;
 
    return position;
}
