#ifndef AXIS_H
#define AXIS_H

typedef struct {
    int ena_pin;
    int dir_pin;
    int pul_pin;
    int max_limit_switch_pin;
    int min_limit_switch_pin;
    int max_limit_switch_position;
    int min_limit_switch_position;
    char axis_label;

} AxisInfo;

typedef struct {
    int position;
    int pins_initialised;
} StepReturnData;

StepReturnData step(AxisInfo, int, int, int);

#endif