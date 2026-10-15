#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void strnCpy(char *t, char *s, int n) {
    int i = 0;
    for (; i < n && s[i]; i++)
        t[i] = s[i];
    t[i] = 0;
}
int main(void) {
    char s[1000], t[1000];
    int n;
    fgets(s, sizeof s, stdin);
    s[strcspn(s, "\r\n")] = 0;
    scanf("%d", &n);
    strnCpy(t, s, n);
    printf("%s", t);
    return 0;
}
