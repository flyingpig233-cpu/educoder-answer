#include<stdlib.h>
#include<stdio.h>
#include "step1_stu.h"
int main()
{
	int randSeed;
    scanf("%d",&randSeed);        //输入整数作为随机数种子
    diceGame(randSeed);
    return 0;
}
