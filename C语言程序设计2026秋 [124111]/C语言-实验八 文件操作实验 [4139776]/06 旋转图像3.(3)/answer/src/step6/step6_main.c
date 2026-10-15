#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
    FILE *in = fopen("matrix.in", "r"), *out = fopen("matrix.out", "w");
    if (!in || !out)
        return 1;
    int n, m;
    if (fscanf(in, "%d%d", &n, &m) != 2)
        return 1;
    int *a = malloc(n * m * sizeof(int));
    for (int i = 0; i < n * m; i++)
        fscanf(in, "%d", a + i);
    for (int j = m - 1; j >= 0; j--) {
        for (int i = 0; i < n; i++)
            fprintf(out, "%s%d", i ? " " : "", a[i * m + j]);
        fputc('\n', out);
    }
    free(a);
    fclose(in);
    fclose(out);
    return 0;
}
