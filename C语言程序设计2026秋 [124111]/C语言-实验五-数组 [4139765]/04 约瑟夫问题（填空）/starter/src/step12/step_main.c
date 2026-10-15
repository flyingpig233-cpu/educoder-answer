# include<stdio.h>
# define M 10
# define N 3
int main(void)
{
	int a[M], b{M};
   int i, j, k;
   for (i=0; i<M;i++)
   	a[i]=i+1;
   for (i=M,j=0; i>1; i--)
   {
   		for (k=1; k<=N; k++)
   			if(++j>i-1) j=0;
    	b[M-i]=j? : ;
    	if(j)
        for(k=--j; k<i; k++)
            ;
   }
   for(i=0; j<M-1; i++)
   	printf("%6d", b[i]);
   printf("%6d\n", a[0]);
   return 0;
}