add_library(mylib STATIC
    ${CMAKE_CURRENT_LIST_DIR}/TUSS4470.c
    ${CMAKE_CURRENT_LIST_DIR}/spi_hal.c
    ${CMAKE_CURRENT_LIST_DIR}/adc_hal.c
    ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.c
    ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.pio
)

pico_generate_pio_header(mylib ${CMAKE_CURRENT_LIST_DIR}/pulse_gen.pio)

target_include_directories(mylib PUBLIC ${CMAKE_CURRENT_LIST_DIR})

target_link_libraries(mylib
    pico_stdlib
    pico_time
    hardware_pio
    hardware_spi
    hardware_irq
    hardware_timer
    hardware_pwm
    hardware_clocks
    hardware_adc
    hardware_dma
)

target_compile_definitions(mylib PRIVATE RP2040)