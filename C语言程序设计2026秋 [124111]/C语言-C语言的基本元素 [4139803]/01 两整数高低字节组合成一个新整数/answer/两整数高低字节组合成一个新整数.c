#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    short k, p;
    scanf("%hd%hd", &k, &p);
    printf("%hd", (short)(((uint16_t)k >> 8) | ((uint16_t)p << 8)));
    return 0;
}
