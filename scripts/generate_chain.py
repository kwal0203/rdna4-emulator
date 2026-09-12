from .validator import VOP2Instructions
from pathlib import Path

import argparse
import yaml
import sys


TEMPLATE = r'''
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

__global__ void v_add_f32_bench(uint32_t *out)
{{
    float x = 1.0f;
    float y = 2.0f;

    uint32_t start = __builtin_amdgcn_s_getreg(0xF81D);;

    asm volatile(
{instructions}
        : "+v"(x)
        : "v"(y));

    uint32_t end = __builtin_amdgcn_s_getreg(0xF81D);;

    if (threadIdx.x == 0)
        out[0] = end - start;
}}


int main()
{{
    uint32_t *d_out = nullptr;
    uint32_t result = 0;

    HIP_CHECK(hipMalloc(&d_out, sizeof(float)));
    hipLaunchKernelGGL(
        v_add_f32_bench,
        dim3(1),
        dim3(32),
        0,
        0,
        d_out);


    HIP_CHECK(hipDeviceSynchronize());
    HIP_CHECK(hipMemcpy(&result, d_out, sizeof(float), hipMemcpyDeviceToHost));
    HIP_CHECK(hipFree(d_out));

    std::cout << "Cycles = " << result << '\n';
}}
'''

parser = argparse.ArgumentParser()
parser.add_argument("--encoding", required=True, help="VOP2, VOP3 etc")
parser.add_argument("--benchmark-type", required=True, help="Latency, throughput etc")
args = parser.parse_args()

with open("/home/kane/Projects/rdna4-emulator/metadata/isa/vop2.yaml", "r") as f:
    raw = yaml.safe_load(f)

instructions = VOP2Instructions.model_validate(raw)
for instruction_name, instruction in instructions.root.items():
    for experiment in instruction.latency_paths:
        if experiment == "vdst_to_src0":
            instruction_text = f"{args.instruction} %0, %0, %1"
        elif experiment == "vdst_to_vsrc1":
            instruction_text = f"{args.instruction} %0, %1, %0"
        else:
            print("Unrecognized experiment")
            sys.exit(1)

        for count in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            instructions_text = "\n".join(
                f'        "{instruction_text}\\n\\t"'
                for _ in range(args.count)
            )
            source = TEMPLATE.format(instructions=instructions)
            out = (
                Path("generated")
                / args.encoding
                / args.benchmark_type
                / experiment.name
                / instruction_name
                / f"n{count}.hip"
            )
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(source)
