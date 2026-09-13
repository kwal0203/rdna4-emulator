from .templates.vdst_src0_vsrc1_f16 import VDST_SRC0_VSRC1_F16
from .templates.vdst_src0_vsrc1_f32 import VDST_SRC0_VSRC1_F32
from .templates.vdst_src0_vsrc1_f64 import VDST_SRC0_VSRC1_F64
from .templates.vdst_src0_vsrc1_b32 import VDST_SRC0_VSRC1_B32
from .templates.vdst_src0_vsrc1_u32 import VDST_SRC0_VSRC1_U32
from .templates.vdst_src0_vsrc1_i32 import VDST_SRC0_VSRC1_I32
from .templates.vdst_sdst_src0_vsrc1_vcc_vector_u32 import VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32
from .templates.vdst_sdst_src0_vsrc1_vcc_carry_u32 import VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32
from .templates.vdst_src0_vsrc1_shift_i32 import VDST_SRC0_VSRC1_SHIFT_I32
from .templates.vdst_src0_vsrc1_carry_false_b32 import VDST_SRC0_VSRC1_CARRY_FALSE_B32
from .templates.vdst_src0_vsrc1_carry_true_b32 import VDST_SRC0_VSRC1_CARRY_TRUE_B32
from .templates.vdst_src0_vsrc1_shift_b32 import VDST_SRC0_VSRC1_SHIFT_B32
from .templates.vdst_src0_vsrc1_shift_b64 import VDST_SRC0_VSRC1_SHIFT_B64

from pydantic import BaseModel, RootModel, model_validator, Field, PrivateAttr
from typing import Self
import yaml


# TEMPLATES = {
#     "VDST_SRC0_VSRC1_F16": VDST_SRC0_VSRC1_F16,
#     "VDST_SRC0_VSRC1_F32": VDST_SRC0_VSRC1_F32,
#     "VDST_SRC0_VSRC1_F64": VDST_SRC0_VSRC1_F64,
#     "VDST_SRC0_VSRC1_LITERAL_F16": VDST_SRC0_VSRC1_LITERAL_F16,
#     "VDST_SRC0_VSRC1_LITERAL_F32": VDST_SRC0_VSRC1_LITERAL_F32,
#     "VDST_SRC0_LITERAL_VSRC1_F16": VDST_SRC0_LITERAL_VSRC1_F16,
#     "VDST_SRC0_LITERAL_VSRC1_F32": VDST_SRC0_LITERAL_VSRC1_F32,
#     "VDST_SRC0_VSRC1_B32": VDST_SRC0_VSRC1_B32,
#     "VDST_SRC0_VSRC1_B64": VDST_SRC0_VSRC1_B64,
#     "VDST_SRC0_VSRC1_U32": VDST_SRC0_VSRC1_U32,
#     "VDST_SRC0_VSRC1_I32": VDST_SRC0_VSRC1_I32,
#     "VDST_SRC0_VSRC1_CARRY_U32": VDST_SRC0_VSRC1_CARRY_U32,
#     "VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32": VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32,
#     "VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32": VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32
# }

TEMPLATES = {
    "VDST_SRC0_VSRC1_F16": VDST_SRC0_VSRC1_F16,
    "VDST_SRC0_VSRC1_F32": VDST_SRC0_VSRC1_F32,
    "VDST_SRC0_VSRC1_F64": VDST_SRC0_VSRC1_F64,
    "VDST_SRC0_VSRC1_B32": VDST_SRC0_VSRC1_B32,
    "VDST_SRC0_VSRC1_U32": VDST_SRC0_VSRC1_U32,
    "VDST_SRC0_VSRC1_I32": VDST_SRC0_VSRC1_I32,
    "VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32": VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32,
    "VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32": VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32,
    "VDST_SRC0_VSRC1_SHIFT_I32": VDST_SRC0_VSRC1_SHIFT_I32,
    "VDST_SRC0_VSRC1_CARRY_FALSE_B32": VDST_SRC0_VSRC1_CARRY_FALSE_B32,
    "VDST_SRC0_VSRC1_CARRY_TRUE_B32": VDST_SRC0_VSRC1_CARRY_TRUE_B32,
    "VDST_SRC0_VSRC1_SHIFT_B32": VDST_SRC0_VSRC1_SHIFT_B32,
    "VDST_SRC0_VSRC1_SHIFT_B64": VDST_SRC0_VSRC1_SHIFT_B64,
}

class Operands(BaseModel):
    inputs: list[str]
    outputs: list[str]

class SpecialStateEntry(BaseModel):
    name: str
    role: str

class SpecialState(BaseModel):
    reads: list[SpecialStateEntry]
    writes: list[SpecialStateEntry]

class LatencyPath(BaseModel):
    name: str
    producer: str
    consumer: str
    instruction_format: str
    template_name: str

    _template_str: str = PrivateAttr()

    @model_validator(mode="after")
    def resolve_template(self) -> Self:
        try:
            self._template_str = TEMPLATES[self.template_name]
        except KeyError as exc:
            raise ValueError(
                f"Unknown template: {self.template_name}"
            ) from exc

        return self

    @property
    def template_str(self) -> Self:
        return self._template_str

class VOP2Instruction(BaseModel):
    encoding: str
    opcode: int = Field(ge=0)
    input_datatype: str
    output_datatype: str
    description: str
    notes: list[str] = Field(default_factory=list)
    operands: Operands
    special_state: SpecialState
    syntax: str
    latency_paths: list[LatencyPath]

    @model_validator(mode="after")
    def validate_latency_paths(self) -> Self:
        producers = set(self.operands.outputs) | {x.name for x in self.special_state.writes}
        consumers = set(self.operands.inputs) | {x.name for x in self.special_state.reads}
        names: list[str] = []
        for path in self.latency_paths:
            if path.producer not in producers:
                raise ValueError(
                    f"Unknown latency path producer: {path.producer}"
                )

            if path.consumer not in consumers:
                raise ValueError(
                    f"Unknown latency path consumer: {path.consumer}"
                )

            expected_name = f"{path.producer}_to_{path.consumer}"
            if path.name != expected_name:
                raise ValueError(
                    f"Latency path name must be: {expected_name}"
                )

            names.append(path.name)

        if len(names) != len(set(names)):
            raise ValueError(f"Latency path names must be unique.")

        return self

class VOP2Instructions(RootModel[dict[str, VOP2Instruction]]):

    @model_validator(mode="after")
    def validate_vop2_instructions(self) -> Self:
        instructions = self.root
        seen_opcodes: dict[int, str] = {}
        for name, instruction in instructions.items():
            if instruction.encoding != "vop2":
                raise ValueError(
                    f"{name}: expected encoding 'vop2', "
                    f"got '{instruction.encoding}'"
                )

            if instruction.opcode in seen_opcodes:
                other = seen_opcodes[instruction.opcode]
                raise ValueError(
                    f"Duplicate opcode: {instruction.opcode}: "
                    f"{other} and {name}."
                )

            seen_opcodes[instruction.opcode] = name

        return self

def load_vop2_instructions(path: str) -> VOP2Instructions:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    return VOP2Instructions.model_validate(raw)
