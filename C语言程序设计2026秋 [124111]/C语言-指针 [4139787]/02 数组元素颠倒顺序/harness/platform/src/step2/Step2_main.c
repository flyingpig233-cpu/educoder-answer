#include"Step2_stu.h"
#define SIZE 100

int main()
{
	/**********  Begin  **********/
	int n,i;
	int arr[SIZE];
	scanf("%d",&n);
	for(i=0;i<n;i++){
		scanf("%d",&arr[i]); 
	} 
    
	reverseOrder(arr,n);
	
	for(i=0;i<n;i++){
		printf("%d ",arr[i]); 
	} 
	
	/**********  End  **********/
	return 0;
}
