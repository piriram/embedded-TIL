#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "algorithm.h"

static const char *evt_name(event_t e) {
    switch (e) {
    case EVT_HARD_ACCEL: return "HARD_ACCEL";
    case EVT_HARD_BRAKE: return "HARD_BRAKE";
    case EVT_SHARP_TURN: return "SHARP_TURN";
    default:             return "NONE";
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <csv>\n", argv[0]);
        return 2;
    }

    FILE *fp = fopen(argv[1], "r");
    if (!fp) { perror("open"); return 1; }

    char line[256];
    int  line_no = 0;
    uint32_t prev_t = 0;
    int  have_prev = 0;

    algo_ctx_t ctx;
    algo_init(&ctx);

    while (fgets(line, sizeof line, fp)) {
        line_no++;
        if (line[0] == '#' || line[0] == '\n') continue;

        uint32_t t_ms;
        int ax, ay, az, gx, gy, gz;
        if (sscanf(line, "%u,%d,%d,%d,%d,%d,%d",
                   &t_ms, &ax, &ay, &az, &gx, &gy, &gz) != 7) {
            fprintf(stderr, "skip bad line %d\n", line_no);
            continue;
        }

        uint32_t dt = have_prev ? (t_ms - prev_t) : 10;
        prev_t = t_ms; have_prev = 1;

        event_t e = algo_step(&ctx,
                              (int16_t)ax, (int16_t)ay, (int16_t)az,
                              (int16_t)gx, (int16_t)gy, (int16_t)gz,
                              dt);
        if (e != EVT_NONE) {
            printf("%u,%s\n", t_ms, evt_name(e));
        }
    }
    fclose(fp);
    return 0;
}
