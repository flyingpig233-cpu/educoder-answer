#ifdef _WIN32
#include <stdint.h>
#include <stdlib.h>
static uint32_t state[31];
static int front = 3, rear = 0;
static uint32_t random_next(void) {
    uint32_t sum = state[front] + state[rear];
    state[front] = sum;
    front = (front + 1) % 31;
    rear = (rear + 1) % 31;
    return sum >> 1;
}
static void random_seed(unsigned seed) {
    if (!seed)
        seed = 1;
    int64_t word = (int32_t)seed;
    state[0] = seed;
    for (int i = 1; i < 31; i++) {
        word = 16807 * (word % 127773) - 2836 * (word / 127773);
        if (word < 0)
            word += 2147483647;
        state[i] = (uint32_t)word;
    }
    front = 3;
    rear = 0;
    for (int i = 0; i < 310; i++)
        random_next();
}
static int sample_rand(void) { return (int)random_next(); }
static void sample_srand(unsigned int seed) { random_seed(seed); }
#define rand sample_rand
#define srand sample_srand
#endif
