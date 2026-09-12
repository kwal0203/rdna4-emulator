from pydantic import BaseModel, RootModel, model_validator, Field
from typing import Self
import yaml


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

class VOP2Instruction(BaseModel):
    encoding: str
    opcode: int = Field(ge=0)
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


with open("/home/kane/Projects/rdna4-emulator/metadata/isa/vop2.yaml", "r") as f:
    raw = yaml.safe_load(f)

instructions = VOP2Instructions.model_validate(raw)
