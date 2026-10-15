#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
struct student {
    int num;
    char name[100];
    double score;
};
void scan(struct student *p, int n) {
    for (int i = 0; i < n; i++, p++)
        scanf("%d%99s%lf", &p->num, p->name, &p->score);
}
void print(struct student *p, int n) {
    for (int i = 0; i < n; i++, p++)
        printf("%d %s %.1f\n", p->num, p->name, p->score);
}
int main(void) {
    struct student s[3];
    scan(s, 3);
    print(s, 3);
    return 0;
}
