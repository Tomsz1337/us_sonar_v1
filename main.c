#include <stdio.h>
#include <stdint.h>

#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

#include "lwip/udp.h"
#include "lwip/ip_addr.h"

#include "mylib/TUSS4470.h"
#include "mylib/spi_hal.h"
#include "hardware/adc.h"
#include "mylib/wifi_hal.h"
#include "hardware/dma.h"

#include "hardware/i2c.h"

// #define NUM_SAMPLES 1000
// #define FRQ_SEL_PIN 9

// TUSS4470_settings sSettings;
// uint8_t tx_buff[2];
// uint8_t rx_buff[2];

// uint16_t captureBuffer[NUM_SAMPLES];

bool reserved_addr(uint8_t addr) {
    return (addr & 0x78) == 0 || (addr & 0x78) == 0x78;
}

int main() 
{
    stdio_init_all(); 
    // udp_init_HAL();
    sleep_ms(3000);
    // //TUSS4470 config////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    // tx_buff[0] = 0x00;
    // tx_buff[1] = 0x00;

    // sSettings.TUSS4470_SPI_Config.baud_rate = 500000;
    // sSettings.TUSS4470_SPI_Config.cpha = 1;
    // sSettings.TUSS4470_SPI_Config.cpol = 0;
    // sSettings.TUSS4470_SPI_Config.csbf = 0;
    // sSettings.TUSS4470_SPI_Config.data_bits = 8;
    // sSettings.TUSS4470_SPI_Config.spi = spi0;

    // sSettings.burstPin = 18;
    // sSettings.nPulses = 16;

    // sSettings.VDRV_CTRL = 0x0F;  
    // sSettings.BPF_CONFIG_1 = 0x1D;
    // sSettings.freqHz = 200000;
    // sSettings.DEV_CTRL_2 = 0x00;
    // sSettings.BURST_PULSE = 0x10;
    // sSettings.ECHO_INT_CONFIG = 0x19;

    // TUSS4470_init(&sSettings, tx_buff);
    //printf("TUSS4470 configuration completed.\n");
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    //ADC setup////
    // adc_init();
    // adc_gpio_init(26);
    // adc_select_input(0);
    // adc_fifo_setup(true, true, 1, false, false);

    // float clkdiv = 48000000.0f / 50000.0f - 96; 
    // adc_set_clkdiv(clkdiv);

    // //DMA setup////
    // uint dma_channel = dma_claim_unused_channel(true);
    // dma_channel_config dmaCfg = dma_channel_get_default_config(dma_channel);

    // channel_config_set_transfer_data_size(&dmaCfg, DMA_SIZE_16);
    // channel_config_set_read_increment(&dmaCfg, false);
    // channel_config_set_write_increment(&dmaCfg, true);

    // channel_config_set_dreq(&dmaCfg, DREQ_ADC);
    

    // sleep_ms(1000);

    i2c_init(i2c_default, 100 * 1000);
    gpio_set_function(PICO_DEFAULT_I2C_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(PICO_DEFAULT_I2C_SDA_PIN);
    gpio_pull_up(PICO_DEFAULT_I2C_SCL_PIN);

    
    printf("\nI2C Bus Scan\n");
    printf("   0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n");

    for (int addr = 0; addr < (1 << 7); ++addr) {
        if (addr % 16 == 0) {
            printf("%02x ", addr);
        }

        int ret;
        uint8_t rxdata;
        if (reserved_addr(addr))
            ret = PICO_ERROR_GENERIC;
        else
            ret = i2c_read_blocking(i2c_default, addr, &rxdata, 1, false);

        printf(ret < 0 ? "." : "@");
        printf(addr % 16 == 15 ? "\n" : "  ");
    }
    printf("Done.\n");
    uint8_t reg = 0x00;
    uint8_t buf[2];
    uint8_t data[2];
    while(1) 
    {  
        // cyw43_arch_poll(); 
        // dma_channel_configure(dma_channel, &dmaCfg, captureBuffer, &adc_hw->fifo, NUM_SAMPLES, false);
        // TUSS4470_trigger(&sSettings, tx_buff);
        // dma_channel_start(dma_channel);
        // adc_run(true);
        // dma_channel_wait_for_finish_blocking(dma_channel);
        // adc_run(false);
        // adc_fifo_drain();
        // udp_send_data_HAL("sp\n");  
        // udp_send_data_uint16_HAL(captureBuffer, NUM_SAMPLES); 
        // udp_send_data_HAL("\n");
        // sleep_ms(100);
      

       // TRIGGER
    buf[0] = 0x0F;
    buf[1] = 0x01;
    i2c_write_blocking(i2c0, 0x40, buf, 2, false);

    sleep_ms(20);

    // SET REGISTER POINTER
    reg = 0x00;
    i2c_write_blocking(i2c0, 0x40, &reg, 1, true);

    // READ TEMP
    i2c_read_blocking(i2c0, 0x40, data, 2, false);

    uint16_t raw = data[0] | (data[1] << 8);
    float temperature = ((float)raw / 65536.0f) * 165.0f - 40.0f;

    uint8_t reg = 0x02;

    i2c_write_blocking(i2c0, 0x40, &reg, 1, true);
    i2c_read_blocking(i2c0, 0x40, data, 2, false);

    uint16_t raw_h = data[0] | (data[1] << 8);
    float humidity = ((float)raw_h / 65536.0f) * 100.0f;
    printf("%.2f, %.2f%%\n", temperature, humidity);
    sleep_ms(2000);
    }
}
