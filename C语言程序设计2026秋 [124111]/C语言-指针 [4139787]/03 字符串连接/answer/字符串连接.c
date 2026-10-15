#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
char *p;
int main0(int argc, char *argv[]) {
    size_t n = 1;
    for (int i = 1; i < argc; i++)
        n += strlen(argv[i]);
    p = malloc(n);
    if (!p)
        return 1;
    *p = 0;
    for (int i = 1; i < argc; i++)
        strcat(p, argv[i]);
    return 0;
}
int main(void) {
    char s[20000], *args[1000];
    int n = 0;
    fgets(s, sizeof s, stdin);
    for (char *t = strtok(s, " \t\r\n"); t; t = strtok(NULL, " \t\r\n"))
        args[n++] = t;
    main0(n, args);
    printf("%s", p);
    free(p);
    return 0;
}
