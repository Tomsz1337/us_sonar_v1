#include "adc_hal.h"
#include "hardware/adc.h"
#include "hardware/dma.h"
#include "hardware/timer.h"
#include "pico/time.h"  // <-- To jest to, czego potrzebujesz



uint16_t analogValues[NUM_SAMPLES];

static volatile int samples_collected = 0;
static int dma_chan;
static alarm_id_t alarm_id;

static bool repeating_timer_callback(struct repeating_timer *rt) {
    if (samples_collected >= NUM_SAMPLES) {
        return false;
    }

    adc_run(true);
    adc_hw->cs |= ADC_CS_START_ONCE_BITS;
    samples_collected++;
    return true;
}

static void start_adc_dma(uint16_t *buffer, size_t count) {
    adc_fifo_drain();
    adc_run(false);
    adc_fifo_setup(
        true,    // Włącz FIFO
        true,    // DREQ (dla DMA)
        1,       // próg
        false,   // bez błędu
        false    // 12-bit
    );
    adc_select_input(0); // GPIO26

    dma_chan = dma_claim_unused_channel(true);
    dma_channel_config cfg = dma_channel_get_default_config(dma_chan);
    channel_config_set_transfer_data_size(&cfg, DMA_SIZE_16);
    channel_config_set_read_increment(&cfg, false);
    channel_config_set_write_increment(&cfg, true);
    channel_config_set_dreq(&cfg, DREQ_ADC);

    dma_channel_configure(
        dma_chan,
        &cfg,
        buffer,
        &adc_hw->fifo,
        count,
        true
    );
}

void adc_dma_timer_capture(void)
{
    samples_collected = 0;
    start_adc_dma(analogValues, NUM_SAMPLES);
    static struct repeating_timer timer;
    add_repeating_timer_us(-SAMPLE_INTERVAL_US, repeating_timer_callback, NULL, &timer);

    dma_channel_wait_for_finish_blocking(dma_chan);
    cancel_repeating_timer(&timer);
    adc_run(false);
}

