#ifndef ALGORITHM_H
#define ALGORITHM_H

#include <stdint.h>

typedef enum {
    EVT_NONE = 0,
    EVT_HARD_ACCEL,
    EVT_HARD_BRAKE,
    EVT_SHARP_TURN,
} event_t;

typedef enum {
    ST_IDLE = 0,
    ST_DETECTING,
    ST_EVENT,
    ST_COOLDOWN,
} state_t;

typedef struct {
    int16_t lpf_buf[8];
    int     lpf_idx;
    int32_t lpf_sum;

    int16_t prev_lpf;

    state_t state;
    int     duration_ms;
    int     cooldown_ms;
    event_t pending;
} algo_ctx_t;

void algo_init(algo_ctx_t *ctx);

event_t algo_step(algo_ctx_t *ctx,
                  int16_t ax, int16_t ay, int16_t az,
                  int16_t gx, int16_t gy, int16_t gz,
                  uint32_t dt_ms);

#endif
