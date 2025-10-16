#include <stdio.h>

int main() {
#ifdef CUDA_AVAILABLE
    printf("CUDA_AVAILABLE is defined\n");
#else
    printf("CUDA_AVAILABLE is NOT defined\n");
#endif

#ifdef OPTIX_AVAILABLE
    printf("OPTIX_AVAILABLE is defined\n");
#else
    printf("OPTIX_AVAILABLE is NOT defined\n");
#endif

    return 0;
}
