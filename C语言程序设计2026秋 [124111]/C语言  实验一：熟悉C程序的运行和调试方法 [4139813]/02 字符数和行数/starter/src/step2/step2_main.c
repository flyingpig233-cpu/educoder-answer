 #include<stdio.h>
int main(void)
{
    char c, numchar, numline;
    numchar = 0;
    numline = 0;
    while((c = getchar()) != EOF){
        numchar++;
        if(c == '\n')
            numline++;
    }
    printf("字符数:%d,", numchar);
    printf("行数:%d", numline);
    return 0;
}