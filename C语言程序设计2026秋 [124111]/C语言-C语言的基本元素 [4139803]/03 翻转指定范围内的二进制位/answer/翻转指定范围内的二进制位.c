#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    int32_t x;
    unsigned p, n;
    scanf("%d%u%u", &x, &p, &n);
    uint32_t mask = n == 32 ? UINT32_MAX : n ? ((UINT32_C(1) << n) - 1) << (p - n + 1) : 0;
    printf("%d", (int32_t)((uint32_t)x ^ mask));
    return 0;
}
