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

#define NUM_SAMPLES 1000
#define FRQ_SEL_PIN 9

TUSS4470_settings sSettings;
uint8_t tx_buff[2];
uint8_t rx_buff[2];

uint16_t analogValues[NUM_SAMPLES];
volatile int pulseCount = 0;
volatile int sampleIndex = 0;

int main() {
    stdio_init_all(); 
    udp_init_HAL();

    //TUSS4470 config////////////////////////////////////////////////////////////////////////////////////////////////////////
    adc_init();
    adc_gpio_init(26);
    adc_select_input(0);

    gpio_init(FRQ_SEL_PIN);
    gpio_set_input_enabled(FRQ_SEL_PIN, 1);
    gpio_pull_up(FRQ_SEL_PIN);
    sleep_ms(10);
    bool modeSelect = gpio_get(FRQ_SEL_PIN);

    tx_buff[0] = 0x00;
    tx_buff[1] = 0x00;

    sSettings.TUSS4470_SPI_Config.baud_rate = 500000;
    sSettings.TUSS4470_SPI_Config.cpha = 1;
    sSettings.TUSS4470_SPI_Config.cpol = 0;
    sSettings.TUSS4470_SPI_Config.csbf = 0;
    sSettings.TUSS4470_SPI_Config.data_bits = 8;
    sSettings.TUSS4470_SPI_Config.spi = spi0;

    sSettings.burstPin = 18;
    sSettings.nPulses = 8;

    if(modeSelect)
    {
        sSettings.BPF_CONFIG_1 = 0x1D;
        sSettings.freqHz = 200000;
    }
    else
    {
        sSettings.BPF_CONFIG_1 = 0x09;
        sSettings.freqHz = 40000;     
    }     
    
    sSettings.DEV_CTRL_2 = 0x00;
    sSettings.VDRV_CTRL = 0x0f;
    sSettings.BURST_PULSE = 0x08;
    sSettings.ECHO_INT_CONFIG = 0x19;

    TUSS4470_init(&sSettings, tx_buff);
    printf("TUSS4470 configuration completed.\n");
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    sleep_ms(1000);

    while(1) 
    {  
        cyw43_arch_poll(); 
        sampleIndex = 0;
        TUSS4470_trigger(&sSettings, tx_buff);
        sleep_us(20);
        for (sampleIndex = 0; sampleIndex < NUM_SAMPLES; sampleIndex++) 
        {
            analogValues[sampleIndex] = adc_read();
            sleep_us(20);
        }
        udp_send_data_HAL("sp\n");  
        udp_send_data_uint16_HAL(analogValues, NUM_SAMPLES); 
        udp_send_data_HAL("\n");
        sleep_ms(100);
    }
    return 1;
}
