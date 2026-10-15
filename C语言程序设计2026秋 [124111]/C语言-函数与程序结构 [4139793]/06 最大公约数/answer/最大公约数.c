#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int gcd(int x, int y) {
    printf("%d %d\n", x, y);
    return y ? gcd(y, x % y) : x;
}
int main(void) {
    int x, y;
    scanf("%d%d", &x, &y);
    printf("%d", gcd(x, y));
    return 0;
}
