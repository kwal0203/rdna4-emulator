
#include <hip/hip_runtime.h>
#include <cstdio>

__global__ void v_add_f32_bench(float *out)
{
    float x = 1.0f;
    float y = 2.0f;

    asm volatile(
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        "v_add_f32 %0, %0, %1\n\t"
        : "+v"(x)
        : "v"(y));

    if (threadIdx.x == 0)
        out[0] = x;
}

int main()
{
    float *d_out = nullptr;
    float result = 0;
    hipMalloc(&d_out, sizeof(float));
    hipLaunchKernelGGL(
        v_add_f32_bench,
        dim3(1),
        dim3(32),
        0,
        0,
        d_out);

    hipDeviceSynchronize();
    hipMemcpy(&result, d_out, sizeof(float), hipMemcpyDeviceToHost);
    hipFree(d_out);
}
