#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    int a, b, c;
    scanf("%d%d%d", &a, &b, &c);
    printf("%d", a > b ? (a > c ? a : c) : (b > c ? b : c));
    return 0;
}
