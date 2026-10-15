#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int mystrlen(const char *s) { return *s ? 1 + mystrlen(s + 1) : 0; }
int main(void) {
    char s[1000];
    scanf("%999s", s);
    printf("%d", mystrlen(s));
    return 0;
}
