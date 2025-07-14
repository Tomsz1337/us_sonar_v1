add_library(mylib STATIC
    ${CMAKE_CURRENT_LIST_DIR}/TUSS4470.c
    ${CMAKE_CURRENT_LIST_DIR}/spi_hal.c
    ${CMAKE_CURRENT_LIST_DIR}/wifi_hal.c
    ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.c
    ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.pio
)
target_compile_definitions(us_sonar_v1 PRIVATE PICO_CYW43_ARCH_POLL)
pico_generate_pio_header(mylib ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.pio)

target_include_directories(mylib PUBLIC ${CMAKE_CURRENT_LIST_DIR})

target_link_libraries(mylib
    pico_stdlib
    pico_cyw43_arch_lwip_poll
    pico_time
    hardware_pio
    hardware_spi
    hardware_irq
    hardware_timer
    hardware_pwm
    hardware_clocks
    hardware_adc
)

target_compile_definitions(mylib PRIVATE RP2040)