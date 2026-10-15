#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void reverseOrder(int *a, int n) {
    for (int *p = a, *q = a + n - 1; p < q; p++, q--) {
        int t = *p;
        *p = *q;
        *q = t;
    }
}
int main(void) {
    int n;
    scanf("%d", &n);
    int *a = malloc(n * sizeof(*a));
    for (int *p = a; p < a + n; p++)
        scanf("%d", p);
    reverseOrder(a, n);
    for (int *p = a; p < a + n; p++)
        printf("%d ", *p);
    free(a);
    return 0;
}
