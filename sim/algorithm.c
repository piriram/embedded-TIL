#include "algorithm.h"

#define LPF_N            8
#define GRAVITY_AZ       16384
#define JERK_HIGH          600
#define GYRO_HIGH        15000
#define MIN_DURATION_MS     50
#define COOLDOWN_MS       1000

static int16_t lpf_step(algo_ctx_t *c, int16_t x) {
    c->lpf_sum -= c->lpf_buf[c->lpf_idx];
    c->lpf_buf[c->lpf_idx] = x;
    c->lpf_sum += x;
    c->lpf_idx = (c->lpf_idx + 1) % LPF_N;
    return (int16_t)(c->lpf_sum / LPF_N);
}

void algo_init(algo_ctx_t *ctx) {
    for (int i = 0; i < LPF_N; i++) ctx->lpf_buf[i] = 0;
    ctx->lpf_idx = 0;
    ctx->lpf_sum = 0;
    ctx->prev_lpf = 0;
    ctx->state = ST_IDLE;
    ctx->duration_ms = 0;
    ctx->cooldown_ms = 0;
    ctx->pending = EVT_NONE;
}

event_t algo_step(algo_ctx_t *ctx,
                  int16_t ax, int16_t ay, int16_t az,
                  int16_t gx, int16_t gy, int16_t gz,
                  uint32_t dt_ms)
{
    (void)ay; (void)az;
    (void)gx; (void)gy;

    int16_t ax_f = lpf_step(ctx, ax);
    int32_t jerk = (int32_t)(ax_f - ctx->prev_lpf);
    ctx->prev_lpf = ax_f;

    event_t emit = EVT_NONE;
    event_t candidate = EVT_NONE;

    if (jerk > JERK_HIGH)            candidate = EVT_HARD_ACCEL;
    else if (jerk < -JERK_HIGH)      candidate = EVT_HARD_BRAKE;
    else if (gz >  GYRO_HIGH ||
             gz < -GYRO_HIGH)        candidate = EVT_SHARP_TURN;

    switch (ctx->state) {
    case ST_IDLE:
        if (candidate != EVT_NONE) {
            ctx->state = ST_DETECTING;
            ctx->pending = candidate;
            ctx->duration_ms = dt_ms;
        }
        break;

    case ST_DETECTING:
        if (candidate == ctx->pending) {
            ctx->duration_ms += dt_ms;
            if (ctx->duration_ms >= MIN_DURATION_MS) {
                ctx->state = ST_EVENT;
                emit = ctx->pending;
                ctx->cooldown_ms = COOLDOWN_MS;
            }
        } else {
            ctx->state = ST_IDLE;
            ctx->duration_ms = 0;
            ctx->pending = EVT_NONE;
        }
        break;

    case ST_EVENT:
        ctx->state = ST_COOLDOWN;
        break;

    case ST_COOLDOWN:
        ctx->cooldown_ms -= (int)dt_ms;
        if (ctx->cooldown_ms <= 0) {
            ctx->state = ST_IDLE;
            ctx->pending = EVT_NONE;
            ctx->duration_ms = 0;
        }
        break;
    }

    return emit;
}
