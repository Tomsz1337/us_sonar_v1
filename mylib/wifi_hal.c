#include "wifi_hal.h"   

struct udp_pcb* udp;
ip_addr_t dest_ip;

void udp_send_data_HAL(const char* msg) 
{
    struct pbuf* p = pbuf_alloc(PBUF_TRANSPORT, strlen(msg), PBUF_RAM);
    if (!p) return;
    memcpy(p->payload, msg, strlen(msg));

    udp_sendto(udp, p, &dest_ip, DEST_PORT);
    pbuf_free(p);
}

void udp_send_data_uint16_HAL(const uint16_t* data, size_t count) 
{
    size_t data_len_bytes = count * sizeof(uint16_t);

    struct pbuf* p = pbuf_alloc(PBUF_TRANSPORT, data_len_bytes, PBUF_RAM);
    if (!p) return;

    memcpy(p->payload, data, data_len_bytes);
    udp_sendto(udp, p, &dest_ip, DEST_PORT);
    pbuf_free(p);
}

int udp_init_HAL(void)
{
    if (cyw43_arch_init()) {
        printf("Wi-Fi init failed\n");
        return -1;
    }

    cyw43_arch_enable_ap_mode(AP_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK);

    IP4_ADDR(&dest_ip, DEST_IP_1, DEST_IP_2, DEST_IP_3, DEST_IP_4);

    udp = udp_new();
    if(!udp)
    {
        printf("Failed to create UDP PCB\n");
        return -1;
    }
    return 0;
}
