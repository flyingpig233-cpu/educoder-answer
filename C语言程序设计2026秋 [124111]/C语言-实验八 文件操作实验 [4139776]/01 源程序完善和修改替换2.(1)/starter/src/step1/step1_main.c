#include<stdio.h>
#include<stdlib.h>
int main(int argc, char* argv[])
{
	FILE * fp;
	if(argc!=2){
		printf("Arguments error!\n");
		exit(-1);
	}
	if((fp=fopen(argv[1],"r"))==NULL){      /* fp指向filename */
		printf("Can't open %s file!\n", argv[1]);
		exit(-1);
	}
	while(!feof(fp))             
		putchar(fgetc(fp));            /* 向显示器中写从filename中读取的字符 */ 
	fclose(fp);                        /* 关闭filename */ 
	return 0;
}
