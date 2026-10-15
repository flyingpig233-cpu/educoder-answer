#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct c_node {
    char data;
    struct c_node *next;
} C_NODE;
void createLinkList(C_NODE **headp, char s[]) {
    C_NODE **p = headp;
    while (*s) {
        *p = malloc(sizeof(C_NODE));
        (*p)->data = *s++;
        (*p)->next = NULL;
        p = &(*p)->next;
    }
}
void judgePalindrome(C_NODE *head) {
    C_NODE *slow = head, *fast = head, *rev = NULL;
    while (fast && fast->next) {
        fast = fast->next->next;
        C_NODE *next = slow->next;
        slow->next = rev;
        rev = slow;
        slow = next;
    }
    if (fast)
        slow = slow->next;
    int ok = 1;
    while (rev) {
        if (rev->data != slow->data)
            ok = 0;
        rev = rev->next;
        slow = slow->next;
    }
    printf(ok ? "true" : "false");
}
int main(void) {
    size_t n = 0, cap = 128;
    char *s = malloc(cap);
    int c;
    while ((c = getchar()) != EOF && c != '\n') {
        if (n + 1 == cap) {
            cap *= 2;
            s = realloc(s, cap);
        }
        s[n++] = c;
    }
    s[n] = 0;
    C_NODE *h = NULL;
    createLinkList(&h, s);
    judgePalindrome(h);
    free(s);
    return 0;
}
