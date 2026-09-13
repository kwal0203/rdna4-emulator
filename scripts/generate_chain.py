from .validator import VOP2Instructions, VOP2Instruction
from .templates.vector_binary_f64 import VECTOR_BINARY_TEMPLATE_F64
from .templates.vector_binary_u32 import VECTOR_BINARY_TEMPLATE_U32
from .templates.vector_binary_i32 import VECTOR_BINARY_TEMPLATE_I32
from .templates.vector_binary_literal_f16 import VECTOR_BINARY_LITERAL_TEMPLATE_F16
from .templates.vector_binary_literal_f32 import VECTOR_BINARY_LITERAL_TEMPLATE_F32
from .templates.vector_carry_u32 import VECTOR_CARRY_TEMPLATE_U32
from .templates.co_ci import VECTOR_BINARY_TEMPLATE_CO_CI

from .templates.vdst_src0_vsrc1_f16 import VECTOR_BINARY_TEMPLATE_F16
from .templates.vdst_src0_vsrc1_f32 import VECTOR_BINARY_TEMPLATE_F32
from .templates.vdst_src0_vsrc1_b32 import VECTOR_BINARY_TEMPLATE_B32


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

LITERALS = {
    "f16": "0x3c00",      # 1.0 in IEEE FP16
    "f32": "0x3f800000",  # 1.0 in IEEE FP32
    "u32": "1",
    "i32": "1",
    "b32": "0x00000001",
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
    "v_add_co_ci_u32": VECTOR_BINARY_TEMPLATE_CO_CI,
    "v_subrev_co_ci_u32": VECTOR_BINARY_TEMPLATE_CO_CI,
    "v_sub_co_ci_u32": VECTOR_BINARY_TEMPLATE_CO_CI,
    "v_add_f16": VECTOR_BINARY_TEMPLATE_F16,
    "v_add_f32": VECTOR_BINARY_TEMPLATE_F32,
    "v_add_f64": VECTOR_BINARY_TEMPLATE_F64,
    "v_add_nc_u32": VECTOR_BINARY_TEMPLATE_U32,
    "v_and_b32": VECTOR_BINARY_TEMPLATE_B32,
}

TEMPLATES = {
    "VDST_SRC0_VSRC1_F16": VECTOR_BINARY_TEMPLATE_F16,
    "VDST_SRC0_VSRC1_F32": VECTOR_BINARY_TEMPLATE_F32,
    "VDST_SRC0_VSRC1_B32": VECTOR_BINARY_TEMPLATE_B32,
}


INSTRUCTION_GROUPS = {
    "VDST_SRC0_VSRC1_F16": {
        "v_add_f16",
        "v_ldexp_f16",
        "v_max_num_f16",
        "v_min_num_f16",
        "v_mul_f16",
        "v_subrev_f16",
        "v_sub_f16",
    },

    "VDST_SRC0_VSRC1_F32": {
        "v_add_f32",
        "v_cvt_pk_rtz_f16_f32",
        "v_max_num_f32",
        "v_min_num_f32",
        "v_mul_dx9_zero_f32",
        "v_mul_f32",
        "v_subrev_f32",
        "v_sub_f32",
    },

    "VDST_SRC0_VSRC1_F64": {
        "todo"
    },

    "VDST_SRC0_VSRC1_B32": {
        "v_and_b32",
        "v_lshlrev_b32"
    },

    "VDST_SRC0_VSRC1_B64": {
        "v_lshlrev_b64"
    },

    "VDST_SRC0_VSRC1_U32": {
        "todo"
    },

    "VDST_SRC0_VSRC1_I32": {
        "todo"
    },

    "VDST_SRC0_VSRC1_LITERAL_F16": {
        "todo"
    },

    "VDST_SRC0_VSRC1_LITERAL_F32": {
        "todo"
    },

    "VDST_SRC0_LITERAL_VSRC1_F16": {
        "v_fmamk_f16"
    },

    "VDST_SRC0_LITERAL_VSRC1_F32": {
        "v_fmamk_f32"
    },

    "VDST_SRC0_VSCR1_VCC_B32": {
        "todo"
    },

    "VDST_SDST_SRC0_VSRC1_VCC_U32": {
        "todo"
    },
}

INSTRUCTION_TO_TEMPLATE = {
    instruction: template_name
    for template_name, instructions in INSTRUCTION_GROUPS.items()
    for instruction in instructions
}

def get_template(instruction_name):
    try:
        template_name = INSTRUCTION_TO_TEMPLATE[instruction_name]
    except KeyError:
        raise ValueError(
            f"No template for instruction: {instruction_name}"
        )

    return TEMPLATES[template_name]

def get_register_width(instruction: VOP2Instruction) -> int:
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
        print(f"Instruction:      {instruction_name}, experiment: {experiment}")
        try:
            template = get_template(instruction_name)
        except KeyError as exc:
            raise ValueError(
                f"Unsupported (family, register_width): ({family}, {instruction.input_datatype})"
                # f"Unsupported (family, register_width): ({family}, {register_width})"
            ) from exc

        # for count in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
        for count in [1]:
            instructions_text = "\n".join(
                f'        "{experiment.instruction_format}\\n\\t"'
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
