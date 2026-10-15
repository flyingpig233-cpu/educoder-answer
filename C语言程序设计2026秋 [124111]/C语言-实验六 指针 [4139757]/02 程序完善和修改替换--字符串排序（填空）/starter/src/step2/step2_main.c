/* 实验6程序完善与修改替换第（1）题源程序：字符串升序排序 */
#include<stdio.h>
#include<________> 
#include<string.h>
#define N 4
/* 对指针数组s指向的size个字符串进行升序排序 */
void strsort ( char *s[ ],int size )
{ 
    ________temp; 
    int i, j ;
    for(i=0; i<size-1; i++)
        for(j=0; j<size-i-1; j++) 
            if ( ________________ )  
{ 
                temp=s[j];
                ______________;    
	               s[j+1]=temp; 
            }
 }

int main( )
{ 
    int i;
    char *s[N], t[50]; 
    for(i=0;i<N;i++)   
{
       gets(t);
       s[i] = (char *)malloc(strlen(t)+1);
       strcpy(_________); 
    }
    strsort(_________);    
    for(i=0;i<N;i++)  puts(s[i]);
    return 0;
}