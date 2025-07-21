#pragma once

#include "spi_hal.h"
#include "pulse_gen.h"
#include "hardware/spi.h"

#ifdef __cplusplus
extern "C" {
#endif

// Register addresses
#define BPF_CONFIG_1_addr       0x10
#define BPF_CONFIG_2_addr       0x11
#define DEV_CTRL_1_addr         0x12
#define DEV_CTRL_2_addr         0x13
#define DEV_CTRL_3_addr         0x14
#define VDRV_CTRL_addr          0x16
#define ECHO_INT_CONFIG_addr    0x17
#define ZC_CONFIG_addr          0x18
#define BURST_PULSE_addr        0x1A
#define TOF_CONFIG_addr         0x1B
#define DEV_STAT_addr           0x1C
#define DEVICE_ID_addr          0x1D
#define REV_ID_addr             0x1E

/// TUSS4470 settings structure
typedef struct {
    SPI_Config TUSS4470_SPI_Config;     // SPI configuration
    PIO_settings sPIO;                  // PIO settings for burst generation
    uint32_t freqHz;                    // Frequency of burst signal
    uint8_t burstPin;                   // Pin used for burst output
    uint8_t nPulses;                    // Number of pulses in burst

    // Register settings
    unsigned char BPF_CONFIG_1;         // 7 BPF_FC_TRIM_FRC | 6 BPF_BYPASS | 5:0 BPF_HPF_FREQ
    unsigned char BPF_CONFIG_2;         // 7:6 RESERVED | 5:4 BPF_Q_SEL | 3:0 BPF_FC_TRIM
    unsigned char DEV_CTRL_1;           // 7 LOGAMP_FRC | 6:4 LOGAMP_SLOPE_ADJ | 3:0 LOGAMP_INT_ADJ
    unsigned char DEV_CTRL_2;           // 7 LOGAMP_DIS_FIRST | 6 LOGAMP_DIS_LAST | 3 RESERVED | 2 VOUT_SCALE_SEL | 1:0 LNA_GAIN
    unsigned char DEV_CTRL_3;           // 4:2 DRV_PLS_FLT_DT | 1:0 IO_MODE
    unsigned char VDRV_CTRL;            // 7 RESERVED | 6 DIS_VDRV_REG_LSTN | 5 VDRV_HI_Z | 4 VDRV_CURRENT_LEVEL | 3:0 VDRV_VOLTAGE_LEVEL
    unsigned char ECHO_INT_CONFIG;      // 7:5 RESERVED | 4 ECHO_INT_CMP_EN | 3:0 ECHO_INT_THR_SEL
    unsigned char ZC_CONFIG;            // 7 ZC_CMP_EN | 6 ZC_EN_ECHO_INT | 5 ZC_CMP_IN_SEL | 4:3 ZC_CMP_STG_SEL | 2:0 ZC_CMP_HYST
    unsigned char BURST_PULSE;          // 7 HALF_BRG_MODE | 6 PRE_DRIVER_MODE | 5:0 BURST_PULSE
    unsigned char TOF_CONFIG;           // 7 SLEEP_MODE_EN | 6 STDBY_MODE_EN | 5:2 RESERVED | 1 VDRV_TRIGGER | 0 CMD_TRIGGER
} TUSS4470_settings;

/// Write one byte to TUSS4470 register
/// \param sSettings Pointer to TUSS4470 settings structure
/// \param addr      Register address
/// \param data      Byte to write
/// \param tx_buff   Transmission buffer (must be at least 2 bytes)
void TUSS4470_write(TUSS4470_settings *sSettings, unsigned char addr, unsigned char data, unsigned char *tx_buff);

/// Read one byte from TUSS4470 register
/// \param sSettings Pointer to TUSS4470 settings structure
/// \param addr      Register address
/// \param tx_buff   Transmission buffer (at least 2 bytes)
/// \param rx_buff   Receive buffer (at least 2 bytes)
void TUSS4470_read(TUSS4470_settings *sSettings, unsigned char addr, unsigned char *tx_buff, unsigned char *rx_buff);

/// Initialize TUSS4470 device with predefined register values
/// \param sSettings Pointer to TUSS4470 settings structure
/// \param tx_buff   Transmission buffer (at least 2 bytes)
void TUSS4470_init(TUSS4470_settings *sSettings, unsigned char *tx_buff);

/// Trigger burst on TUSS4470 using configured PIO and burst parameters
/// \param sSettings Pointer to TUSS4470 settings structure
/// \param tx_buff   Transmission buffer (at least 2 bytes)
void TUSS4470_trigger(TUSS4470_settings *sSettings, uint8_t *tx_buff);

#ifdef __cplusplus
}
#endif
