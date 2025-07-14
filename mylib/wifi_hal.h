#pragma once

#include "pico/cyw43_arch.h"
#include "lwip/udp.h"
#include "lwip/ip_addr.h"

#ifdef __cplusplus
extern "C" {
#endif

#define AP_SSID "PICO_NET"
#define WIFI_PASSWORD "test1234"
#define DEST_IP_1   192
#define DEST_IP_2   168
#define DEST_IP_3   4
#define DEST_IP_4   2
#define DEST_PORT   5005

/// Initialise WIFI AP and create UDP PCB
/// \return Returns 0 for succes and error code otherwise
int udp_init_HAL(void);

/// Sends data to IP adress set by udp_init() and DEST_PORT
/// @param msg pointer to const char array with data to send
void udp_send_data_HAL(const char* msg);

/// Sends data to IP adress set by udp_init() and DEST_PORT 
/// @param data pointer to const uint16_t array with data to send
/// @param count number of elements in data array
void udp_send_data_uint16_HAL(const uint16_t* data, size_t count);

#ifdef __cplusplus
}
#endif