from pathlib import Path
import argparse


TEMPLATE = r'''
#include <hip/hip_runtime.h>
#include <cstdio>

__global__ void v_add_f32_bench(float *out)
{{
    float x = 1.0f;
    float y = 2.0f;

    asm volatile(
{instructions}
        : "+v"(x)
        : "v"(y));

    if (threadIdx.x == 0)
        out[0] = x;
}}

int main()
{{
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
}}
'''

parser = argparse.ArgumentParser()
parser.add_argument("--encoding", required=True, help="VOP2, VOP3 etc")
parser.add_argument("--benchmark-type", required=True, help="Latency, throughput etc")
parser.add_argument("--experiment", required=True, help="a_to_b")
parser.add_argument("--instruction", required=True, help="v_add_f32 etc")
parser.add_argument("--count", type=int, required=True, help="Chain length")
args = parser.parse_args()

instruction = f"{args.instruction} %0, %0, %1"
instructions = "\n".join(
    f'        "{instruction}\\n\\t"'
    for _ in range(args.count)
)

source = TEMPLATE.format(instructions=instructions)

print(args.benchmark_type)

out = (
    Path("generated")
    / args.encoding
    / args.benchmark_type
    / args.experiment
    / args.instruction
    / f"n{args.count}.cpp"
)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source)
