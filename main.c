#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/udp.h"
#include "lwip/ip_addr.h"
#include <stdint.h>
#include <stdio.h>
#include "pico/stdlib.h"
#include "mylib/TUSS4470.h"
#include "mylib/spi_hal.h"
#include "hardware/timer.h"
#include "hardware/adc.h"
#include "hardware/uart.h"
#include "mylib/adc_hal.h"

#define WIFI_SSID "UniFi Network 2.4"
#define WIFI_PASSWORD "test1234"
#define DEST_IP_1   192
#define DEST_IP_2   168
#define DEST_IP_3   100
#define DEST_IP_4   126
#define DEST_PORT   5005

#define NUM_SAMPLES 1000
#define FRQ_SEL_PIN 9

struct udp_pcb* udp;
ip_addr_t dest_ip;

void udp_send_data(const char* msg) 
{
    struct pbuf* p = pbuf_alloc(PBUF_TRANSPORT, strlen(msg), PBUF_RAM);
    if (!p) return;
    memcpy(p->payload, msg, strlen(msg));

    udp_sendto(udp, p, &dest_ip, DEST_PORT);
    pbuf_free(p);
}

void udp_send_data_uint16(const uint16_t* data, size_t count) {
    size_t data_len_bytes = count * sizeof(uint16_t);

    struct pbuf* p = pbuf_alloc(PBUF_TRANSPORT, data_len_bytes, PBUF_RAM);
    if (!p) return;

    memcpy(p->payload, data, data_len_bytes);
    udp_sendto(udp, p, &dest_ip, DEST_PORT);
    pbuf_free(p);
}


TUSS4470_settings sSettings;
uint8_t tx_buff[2];
uint8_t rx_buff[2];

uint16_t analogValues[NUM_SAMPLES];
volatile int pulseCount = 0;
volatile int sampleIndex = 0;

int main() {
    stdio_init_all();
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //UDP connenction config////////////////////////////////////////////////////////////////////////////////////////////////
    if (cyw43_arch_init()) {
        printf("Wi-Fi init failed\n");
        return -1;
    }

    cyw43_arch_enable_sta_mode();

    printf("Connecting to Wi-Fi...\n");
    int err = cyw43_arch_wifi_connect_timeout_ms("UniFi Network 2.4", "test1234", CYW43_AUTH_WPA2_AES_PSK, 30000);
    if(err) {
        printf("Wi-Fi connect failed, error: %d\n", err);
        return -1;
    }

    printf("Connected.\n");

    udp = udp_new();
    if(!udp)
    {
        printf("Failed to create UDP PCB\n");
        return -1;
    }
    IP4_ADDR(&dest_ip, DEST_IP_1, DEST_IP_2, DEST_IP_3, DEST_IP_4);
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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
        udp_send_data("sp\n");  
        udp_send_data_uint16(analogValues, NUM_SAMPLES); 
        udp_send_data("\n");
        sleep_ms(100);
    }
    return 1;
}
