#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/udp.h"
#include "lwip/ip_addr.h"

#define WIFI_SSID "UniFi Network 2.4"
#define WIFI_PASSWORD "test1234"

void send_udp_message() {
    struct udp_pcb* pcb = udp_new();
    if (!pcb) return;

    ip_addr_t dest_ip;
    IP4_ADDR(&dest_ip, 192, 168, 100, 126); // IP twojego komputera

    struct pbuf* p = pbuf_alloc(PBUF_TRANSPORT, 12, PBUF_RAM);
    if (!p) return;
    memcpy(p->payload, "Hello Pico!", 12);

    udp_sendto(pcb, p, &dest_ip, 5005); // port 5005
    pbuf_free(p);
    udp_remove(pcb);
}

int main() {
    stdio_init_all();

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
    sleep_ms(2000);
    send_udp_message();

    while (true) {
        cyw43_arch_poll(); // obowiązkowe w trybie PICO_CYW43_ARCH_POLL
        sleep_ms(10);
        send_udp_message();
    }
}
