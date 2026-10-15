#include<stdio.h>

#include"step6_stu.h"

//请根据此主函数流程，使用递归补全step6_stu.h文件中gcd()函数

int main() {
		int x,y;
		
		scanf("%d%d",&x,&y);
		printf("%d",gcd(x,y));
		
		return 0;
}