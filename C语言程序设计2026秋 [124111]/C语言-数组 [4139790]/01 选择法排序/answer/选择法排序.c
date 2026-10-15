#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    int n;
    scanf("%d", &n);
    int *a = malloc((size_t)n * sizeof(*a));
    for (int i = 0; i < n; i++)
        scanf("%d", a + i);
    for (int i = 0; i < n; i++) {
        int k = i;
        for (int j = i + 1; j < n; j++)
            if (a[j] < a[k])
                k = j;
        int t = a[i];
        a[i] = a[k];
        a[k] = t;
    }
    for (int i = 0; i < n; i++)
        printf("%d ", a[i]);
    free(a);
    return 0;
}
