#define NUM_SAMPLES 1000
#define SAMPLE_INTERVAL_US 20  // 20us = 50kHz
#include <stdint.h>
#include "pico/stdlib.h"

void adc_dma_timer_capture(void);
static void start_adc_dma(uint16_t *buffer, size_t count);
