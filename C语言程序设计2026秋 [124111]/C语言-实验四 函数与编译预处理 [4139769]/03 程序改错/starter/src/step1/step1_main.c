#include<stdio.h>
int main(void)
{
	int k;
	for(k=1; k<=20; k++)
		printf("k=%d the sum is %ld\n",k,sum_fac(k));
	return 0;
}
long sum_fac(int n){
	long s=0;
	int i, fac;
	for(i=1;i<=n;i++) fac*=i;
	s+=fac;
	return s;
}