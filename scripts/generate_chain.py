from .validator import VOP2Instructions
from .templates.vector_binary import VECTOR_BINARY_TEMPLATE
from .templates.carry import CARRY_TEMPLATE
from pathlib import Path

import argparse
import yaml
import sys

EXPERIMENTS = {
    "vdst_to_src0": {
        "template": VECTOR_BINARY_TEMPLATE,
        "instruction": "{instruction} %0, %0, %1",
    },
    "vdst_to_vsrc1": {
        "template": VECTOR_BINARY_TEMPLATE,
        "instruction": "{instruction} %0, %1, %0",
    },
    "sdst_to_vcc": {
        "template": CARRY_TEMPLATE,
        "instruction": "{instruction} %0, %1, %2, %3, %1",
    },
    "vdst_to_vdst": {
        "template": VECTOR_BINARY_TEMPLATE,
        "instruction": "{instruction} %0, %0, %1",
    },
}

parser = argparse.ArgumentParser()
parser.add_argument("--encoding", required=True, help="VOP2, VOP3 etc")
parser.add_argument("--benchmark-type", required=True, help="Latency, throughput etc")
args = parser.parse_args()

with open("/home/kane/Projects/rdna4-emulator/metadata/isa/vop2.yaml", "r") as f:
    raw = yaml.safe_load(f)

instructions = VOP2Instructions.model_validate(raw)
for instruction_name, instruction in instructions.root.items():
    for experiment in instruction.latency_paths:
        print(f"Instruction: {instruction_name}, experiment: {experiment}")
        try:
            config = EXPERIMENTS[experiment.name]
        except KeyError:
            print("Unrecognized experiment")
            print(f"Instruction: {instruction_name}, experiment: {experiment.name}")
            sys.exit(1)

        template = config["template"]
        instruction_text = config["instruction"].format(instruction=instruction_name)
        for count in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            instructions_text = "\n".join(
                f'        "{instruction_text}\\n\\t"'
                for _ in range(count)
            )

            source = template.format(
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
