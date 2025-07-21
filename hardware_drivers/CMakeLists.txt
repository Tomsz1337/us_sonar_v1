add_library(hardware_drivers STATIC
    ${CMAKE_CURRENT_LIST_DIR}/TUSS4470.c
    ${CMAKE_CURRENT_LIST_DIR}/spi_hal.c
    ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.c
    ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.pio
)
target_compile_definitions(hardware_drivers PRIVATE PICO_CYW43_ARCH_POLL)
pico_generate_pio_header(hardware_drivers ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.pio)

target_include_directories(hardware_drivers PUBLIC ${CMAKE_CURRENT_LIST_DIR})

target_link_libraries(hardware_drivers
    pico_stdlib
    pico_time
    hardware_pio
    hardware_spi
    hardware_irq
    hardware_timer
    hardware_pwm
    hardware_clocks
    hardware_adc
)

target_compile_definitions(hardware_drivers PRIVATE RP2040)