#include"Step2_stu.h"
int main()
{
	/**********  Begin  **********/
 
    char buf[1024];
    char *file1="src/step2_1/test1.c";   // 源文件1
    char *file2="src/step2_1/test2.c";   // 源文件2
    char *file3="src/step2_1/test3.c";   // 源文件3
    char *file="src/step2_1/test.c";     // 目标文件
    FILE *fp;                            // 目标文件的指针
    
    connect(file,file1,file2,file3);    // 将源文件file1、file2和file3的内容连接到目标文件file中
    
    fp=fopen("src/step2_1/test.c","r");
    while(fgets(buf,sizeof(buf),fp)!=NULL)   //读取目标文件
    {
        printf("%s",buf);
    }
    fclose(fp);
    fp=fopen("src/step2_1/test.c","w");
    fclose(fp);
	/**********   End   **********/
	return 0; 
}