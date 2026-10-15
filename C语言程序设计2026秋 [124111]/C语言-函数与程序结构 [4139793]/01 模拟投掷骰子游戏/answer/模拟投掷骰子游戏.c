#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Portable implementation of the glibc default random sequence, for Windows sample parity.
   Algorithm reference: https://sourceware.org/git/?p=glibc.git;a=blob;f=stdlib/random_r.c */
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
void diceGame(int randSeed) {
    random_seed((unsigned)randSeed);
    int point = 0;
    for (int round = 1;; round++) {
        int a = random_next() % 6 + 1, b = random_next() % 6 + 1, score = a + b;
        int success = round == 1 ? (score == 7 || score == 11) : score == point;
        int failed = round == 1 ? (score == 2 || score == 3 || score == 12) : score == 7;
        printf("Round %d:  Score:%d  %s!\n", round, score,
               success  ? "Success"
               : failed ? "Failed"
                        : "Continue");
        if (success || failed)
            break;
        if (round == 1) {
            point = score;
            printf("Next rounds: Score %d:Success, Score 7:Failed, others:Continue\n", point);
        }
    }
}
int main(void) {
    int seed;
    scanf("%d", &seed);
    diceGame(seed);
    return 0;
}
