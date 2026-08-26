#ifndef AXIS_H
#define AXIS_H

typedef struct {
    int ena_pin;
    int dir_pin;
    int pul_pin;
    char axis_label;
} AxisInfo;

typedef struct {
    int position;
    int pins_initialised;
} StepReturnData;

StepReturnData step(AxisInfo, int, int, int);

#endif