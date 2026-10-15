#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void bubble_sort(int *a, int n) {
    for (int i = 0; i < n; i++)
        for (int *p = a; p < a + n - i - 1; p++)
            if (*p > *(p + 1)) {
                int t = *p;
                *p = *(p + 1);
                *(p + 1) = t;
            }
}
int main(void) {
    int a[10];
    for (int *p = a; p < a + 10; p++)
        scanf("%d", p);
    bubble_sort(a, 10);
    for (int *p = a; p < a + 10; p++)
        printf("%d ", *p);
    return 0;
}
