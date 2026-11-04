#ifndef UTILS_H
#define UTILS_H

extern "C" void init_clock();

uint8_t findAddress();

uint8_t setupPorts(uint8_t pullups);

uint8_t setupADC();

#endif