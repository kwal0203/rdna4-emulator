from .validator import VOP2Instructions, VOP2Instruction
from .templates.vector_binary_f32 import VECTOR_BINARY_TEMPLATE_F32
from .templates.vector_binary_f64 import VECTOR_BINARY_TEMPLATE_F64
from .templates.vector_binary_literal_f16 import VECTOR_BINARY_LITERAL_TEMPLATE_F16
from .templates.carry_u32 import CARRY_TEMPLATE_U32
from pathlib import Path

import subprocess
import argparse
import yaml
import sys


REGISTER_WIDTH = {
    "f16": 32,
    "i16": 32,
    "u16": 32,
    "b16": 32,
    "i24": 32,
    "u24": 32,
    "f32": 32,
    "i32": 32,
    "u32": 32,
    "b32": 32,
    "f64": 64,
    "i64": 64,
    "u64": 64,
    "b64": 64,
}

EXPERIMENTS = {
    "vdst_to_src0": {
        "family": "vector_binary",
        "instruction": "{instruction} %0, %0, %1",
    },
    "vdst_to_vsrc1": {
        "family": "vector_binary",
        "instruction": "{instruction} %0, %1, %0",
    },
    "sdst_to_vcc": {
        "family": "carry",
        "instruction": "{instruction} %0, %1, %2, %3, %1",
    },
    "vdst_to_vdst": {
        "family": "vector_binary",
        "instruction": "{instruction} %0, %0, %1",
    },
}

TEMPLATES = {
    ("vector_binary", 32): VECTOR_BINARY_TEMPLATE_F32,
    ("vector_binary", 64): VECTOR_BINARY_TEMPLATE_F64,
    ("vector_binary_literal", 32): VECTOR_BINARY_LITERAL_TEMPLATE_F16,
    ("carry", 32): CARRY_TEMPLATE_U32,
}

def get_register_width(instruction: VOP2Instruction) -> str:
    try:
        return REGISTER_WIDTH[instruction.input_datatype]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported input datatype: {instruction.input_datatype}"
        ) from exc

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
            family = config["family"]
            instruction_format = config["instruction"]

            format_args = {
                "instruction": instruction_name
            }

            if "literal" in instruction.syntax:
                family += "_literal"
                instruction_format += ", {literal}"
                format_args["literal"] = "0x3c00"

            instruction_text = instruction_format.format(**format_args)
            register_width = get_register_width(instruction)

        except KeyError as exc:
            raise ValueError(
                f"Unsupported experiment {experiment.name}"
            ) from exc

        try:
            template = TEMPLATES[(family, register_width)]

        except KeyError as exc:
            raise ValueError(
                f"Unsupported (family, register_width): ({family}, {register_width})"
            ) from exc

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

            hipcc = "/opt/rocm/core-10.0/bin/hipcc"
            exe = str(out.with_suffix(""))
            print(f"    Compiling {exe.split('/')[-1]}")
            subprocess.run(
                [hipcc, str(out), "-o", exe],
                check=True
            )
