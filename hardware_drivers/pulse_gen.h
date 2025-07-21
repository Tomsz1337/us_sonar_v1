#pragma once

#include "hardware/pio.h"

#ifdef __cplusplus
extern "C" {
#endif

/// Configuration struct for PIO state machine
typedef struct PIO_settings
{
    PIO pio;    ///< PIO instance (pio0/pio1)
    uint sm;    ///< State machine number(0-3)
}PIO_settings;

/// Initiazlie PIO program
/// \param sPIO     Pointer to PIO_settings struct
/// \param freqHz   Frequency of generatet pulses in Hz  
/// \param pin      Output pin
void pulse_gen_program_init(PIO_settings *sPIO, uint32_t freqHz, uint pin);

/// Starts pulse generation
/// \param pio        PIO instance (pio0/pio1)
/// \param sm         State machine number(0-3)
/// \param npulses    Number of pulses to generate
void pulse_gen_start(PIO_settings *sPIO, uint32_t nPulses);

#ifdef __cplusplus
}
#endif
