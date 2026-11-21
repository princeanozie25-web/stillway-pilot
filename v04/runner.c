/* v0.4 table runner: one program for exact and learned planner tables (same format, widths, caching, loop).
 *
 *   cc -O2 -o v04/runner v04/runner.c
 *   v04/runner tables.bin jobs.bin out.bin MODE REPEAT PASSES
 *
 * tables.bin  (stillway4/gates.py write_tables): int32 magic, G, n_codes, NL, NS, code_bytes; term[3^G]; cell[n*NL]; route[n*NL*NS] (uint8)
 * jobs.bin    int32 n_jobs, lmax; per job: int32 q, gates, L, legs[lmax]   (legs[0] is the current leg)
 * MODE 0      one decision per job: the route at legs[0]
 * MODE 1      the whole job: a route at every leg, the gates updated by the route taken (the sweep is redone at every leg)
 * MODE 2, 3   as 0 and 1, by the exact dynamic program computed on the spot (no cell or route table is read)
 * Each job is timed as one call (batch one).  The call is repeated REPEAT times inside the timer and the mean is stored.
 * out.bin     int32 n_jobs, passes; uint8 first_route[n_jobs]; uint8 final_gates[n_jobs]; float32 ns[passes][n_jobs]
 * stdout      load time in ns, peak resident bytes, table bytes
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>

static inline uint64_t now_ns(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec; }

static int32_t G, N, NL, NS, CB, NT;
static uint8_t *term8, *cell8, *route;
static inline uint32_t code_at(const uint8_t *p, size_t i) { return CB == 2 ? ((const uint16_t *)p)[i] : ((const uint32_t *)p)[i]; }

static inline int decide(int q, int s, int L, const int32_t *legs) {
    uint32_t c = code_at(term8, (size_t)q);
    for (int j = L - 1; j >= 1; j--) c = code_at(cell8, (size_t)c * NL + legs[j]);
    return route[((size_t)c * NL + legs[0]) * NS + s];
}
static inline int apply_trip(int s, int trip) {
    int e = trip / G, g = trip % G, bit = 1 << (G - 1 - g);
    if (e == 1) return s ^ bit; if (e == 2) return s | bit; if (e == 3) return s & ~bit; return s;
}

/* the exact planner with no tables: the reverse dynamic program done on the spot (MODE 2 and 3) */
static inline int decide_dp(int q, int s, int L, const int32_t *legs) {
    uint8_t T[64], U[64]; int req[8]; for (int g = G - 1; g >= 0; g--) { req[g] = q % 3; q /= 3; }
    for (int st = 0; st < NS; st++) { int c = 0; for (int g = 0; g < G; g++) if (req[g] && ((st >> (G - 1 - g)) & 1) == req[g] - 1) c++; T[st] = (uint8_t)c; }
    for (int j = L - 1; j >= 1; j--) { int a = legs[j] / NT, b = legs[j] % NT;
        for (int st = 0; st < NS; st++) { uint8_t x = T[apply_trip(st, a)], y = T[apply_trip(st, b)]; U[st] = x > y ? x : y; }
        memcpy(T, U, NS); }
    return T[apply_trip(s, legs[0] % NT)] > T[apply_trip(s, legs[0] / NT)];
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: runner tables jobs out MODE REPEAT PASSES\n"); return 2; }
    int mode = atoi(argv[4]), repeat = atoi(argv[5]), passes = atoi(argv[6]);
    uint64_t t0 = now_ns();
    FILE *f = fopen(argv[1], "rb"); if (!f) return 3; fseek(f, 0, SEEK_END); long tb = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *buf = malloc(tb); if (fread(buf, 1, tb, f) != (size_t)tb) return 3; fclose(f);
    int32_t *h = (int32_t *)buf; if (h[0] != 0x53544C57) return 4; G = h[1]; N = h[2]; NL = h[3]; NS = h[4]; CB = h[5]; NT = 4 * G;
    size_t NQ = 1; for (int i = 0; i < G; i++) NQ *= 3;
    term8 = buf + 24; cell8 = term8 + NQ * CB; route = cell8 + (size_t)N * NL * CB;
    uint64_t load_ns = now_ns() - t0;
    f = fopen(argv[2], "rb"); if (!f) return 3; int32_t hd[2]; if (fread(hd, 4, 2, f) != 2) return 3; int n = hd[0], lmax = hd[1]; size_t rec = 3 + lmax;
    int32_t *jobs = malloc((size_t)n * rec * 4); if (fread(jobs, 4, (size_t)n * rec, f) != (size_t)n * rec) return 3; fclose(f);
    uint8_t *first = malloc(n), *fin = malloc(n); float *ns = malloc(sizeof(float) * (size_t)n * passes); volatile int sink = 0;
    for (int p = 0; p < passes; p++) for (int i = 0; i < n; i++) {
        const int32_t *J = jobs + (size_t)i * rec; int q = J[0], L = J[2]; const int32_t *legs = J + 3; int r0 = 0, s = J[1];
        uint64_t a = now_ns();
        for (int k = 0; k < repeat; k++) {
            s = J[1];
            if (mode == 0) { r0 = decide(q, s, L, legs); }
            else if (mode == 2) { r0 = decide_dp(q, s, L, legs); }
            else for (int i2 = 0; i2 < L; i2++) { int r = mode == 1 ? decide(q, s, L - i2, legs + i2) : decide_dp(q, s, L - i2, legs + i2); if (i2 == 0) r0 = r; int leg = legs[i2]; s = apply_trip(s, r ? leg % NT : leg / NT); }
            sink += r0;
        }
        uint64_t b = now_ns(); ns[(size_t)p * n + i] = (float)(b - a) / repeat; first[i] = (uint8_t)r0; fin[i] = (uint8_t)s;
    }
    f = fopen(argv[3], "wb"); int32_t oh[2] = {n, passes}; fwrite(oh, 4, 2, f); fwrite(first, 1, n, f); fwrite(fin, 1, n, f); fwrite(ns, sizeof(float), (size_t)n * passes, f); fclose(f);
    struct rusage ru; getrusage(RUSAGE_SELF, &ru);
    printf("{\"load_ns\": %llu, \"peak_rss_bytes\": %ld, \"table_bytes\": %ld, \"n_codes\": %d, \"jobs\": %d}\n", (unsigned long long)load_ns, (long)ru.ru_maxrss, tb, N, n);
    return 0;
}
