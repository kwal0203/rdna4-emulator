CARRY_TEMPLATE = r'''
#include <hip/hip_runtime.h>
#include <iostream>

#define HIP_CHECK(call)                                 \
    do {{                                                \
        hipError_t err = call;                          \
        if (err != hipSuccess) {{                        \
            std::cerr << #call << " failed " << '\n';   \
            return 1;                                   \
        }}                                               \
    }} while (0)                                         \

__global__ void {{instruction_name}}_bench(uint32_t *out)
{{
    uint32_t result;
    uint32_t carry;
    uint32_t x;
    uint32_t y;

    uint32_t start = __builtin_amdgcn_s_getreg(0xF81D);;

    asm volatile(
{instructions}
        : "+v"(result), "+s"(carry)
        : "v"(x), "v"(y));

    uint32_t end = __builtin_amdgcn_s_getreg(0xF81D);;

    if (threadIdx.x == 0)
        out[0] = end - start;
}}


int main()
{{
    uint32_t *d_out = nullptr;
    uint32_t result = 0;

    HIP_CHECK(hipMalloc(&d_out, sizeof(uint32_t)));
    hipLaunchKernelGGL(
        v_add_f32_bench,
        dim3(1),
        dim3(32),
        0,
        0,
        d_out);

    HIP_CHECK(hipDeviceSynchronize());
    HIP_CHECK(hipMemcpy(&result, d_out, sizeof(uint32_t), hipMemcpyDeviceToHost));
    HIP_CHECK(hipFree(d_out));

    std::cout << "Cycles = " << result << '\n';
}}
'''