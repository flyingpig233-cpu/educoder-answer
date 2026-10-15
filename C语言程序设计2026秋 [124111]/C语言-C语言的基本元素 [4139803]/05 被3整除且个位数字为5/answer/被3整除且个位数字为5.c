#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    unsigned a;
    scanf("%u", &a);
    printf("%d", a % 3 == 0 && a % 10 == 5);
    return 0;
}
