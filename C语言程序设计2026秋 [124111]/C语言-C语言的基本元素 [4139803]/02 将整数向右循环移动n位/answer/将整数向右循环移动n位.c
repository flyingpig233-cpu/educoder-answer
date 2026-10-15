#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    int32_t x;
    unsigned n;
    scanf("%d%u", &x, &n);
    n %= 32;
    uint32_t u = (uint32_t)x;
    if (n)
        u = (u >> n) | (u << (32 - n));
    printf("%d", (int32_t)u);
    return 0;
}
