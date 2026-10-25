#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static FILE *out;
#define printf(...) fprintf(out,__VA_ARGS__)
static volatile uintptr_t sink;
typedef HANDLE (WINAPI *heap_t)(void);
typedef DWORD (WINAPI *err_t)(void);
typedef void (WINAPI *set_t)(DWORD);
typedef BOOL (WINAPI *qpc_t)(LARGE_INTEGER*);
static double seconds(LARGE_INTEGER a,LARGE_INTEGER b,LARGE_INTEGER f){return (double)(b.QuadPart-a.QuadPart)/f.QuadPart;}
int main(int argc,char **argv){
 if(argc!=2)return 4; out=fopen(argv[1],"w");if(!out)return 5; fprintf(out,"BENCH_STARTED\n");fflush(out);
 LARGE_INTEGER freq,a,b,q; QueryPerformanceFrequency(&freq);
 HMODULE modules[2]={GetModuleHandleW(L"kernel32.dll"),GetModuleHandleW(L"kernelbase.dll")};
 const int n=2000000;
 for(int round=0;round<3;round++)for(int k=0;k<2;k++){
  heap_t heap=(heap_t)GetProcAddress(modules[k],"GetProcessHeap");err_t err=(err_t)GetProcAddress(modules[k],"GetLastError");set_t set=(set_t)GetProcAddress(modules[k],"SetLastError");qpc_t counter=(qpc_t)GetProcAddress(modules[k],"QueryPerformanceCounter");
  if(!heap||!err||!set||!counter)return 2;
  for(int i=0;i<10000;i++){sink=(uintptr_t)heap();set(i);sink=err();counter(&q);}
  QueryPerformanceCounter(&a);for(int i=0;i<n;i++)sink=(uintptr_t)heap();QueryPerformanceCounter(&b);printf("round=%d module=%s GetProcessHeap_ns=%.2f ",round,k?"kernelbase":"kernel32",seconds(a,b,freq)*1e9/n);
  QueryPerformanceCounter(&a);for(int i=0;i<n;i++){set(i);sink=err();}QueryPerformanceCounter(&b);printf("SetGetLastError_pair_ns=%.2f ",seconds(a,b,freq)*1e9/n);
  QueryPerformanceCounter(&a);for(int i=0;i<n;i++)counter(&q);QueryPerformanceCounter(&b);printf("QueryPerformanceCounter_ns=%.2f\n",seconds(a,b,freq)*1e9/n);fflush(out);
 }
 QueryPerformanceCounter(&a);for(int i=0;i<1000000;i++){void*p=malloc(128);if(!p)return 3;sink=(uintptr_t)p;free(p);}QueryPerformanceCounter(&b);printf("CRT_malloc_free_pair_ns=%.2f\n",seconds(a,b,freq)*1e9/1000000);
 fclose(out); return 0;
}
