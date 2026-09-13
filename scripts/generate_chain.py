from .validator import load_vop2_instructions
from pathlib import Path

import subprocess
import argparse


LITERALS = {
    "f16": "0x3c00",      # 1.0 in IEEE FP16
    "f32": "0x3f800000",  # 1.0 in IEEE FP32
    "u32": "1",
    "i32": "1",
    "b32": "0x00000001",
}

parser = argparse.ArgumentParser()
parser.add_argument("--encoding", required=True, help="VOP2, VOP3 etc")
parser.add_argument("--benchmark-type", required=True, help="Latency, throughput etc")
args = parser.parse_args()

instructions = load_vop2_instructions("/home/kane/Projects/rdna4-emulator/metadata/isa/vop2.yaml")
for instruction_name, instruction in instructions.root.items():
    for experiment in instruction.latency_paths:
        print(f"Instruction:      {instruction_name}, experiment: {experiment}")

        # for count in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
        for count in [1]:
            instructions_text = "\n".join(
                f'        "{experiment.instruction_format}\\n\\t"'
                for _ in range(count)
            )

            source = instruction.template_str.format(
                instruction_name=instruction_name,
                instructions=instructions_text)

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

            hipcc = "/opt/rocm/core-10.0/bin/hipcc"
            exe = str(out.with_suffix(""))
            print(f"    Compiling {exe.split('/')[-1]}")
            subprocess.run(
                [hipcc, str(out), "-o", exe],
                check=True
            )
