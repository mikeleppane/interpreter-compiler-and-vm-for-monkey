from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import TypeAlias

Opcode: TypeAlias = int


@dataclass(frozen=True)
class Instructions:
    inst: list[int] = field(default_factory=list)

    def to_string(self) -> str:
        output: str = ""

        i: int = 0
        while i < len(self.inst):
            definition = lookup(self.inst[i])
            if definition is None:
                output += f"ERROR: Unknown opcode {self.inst[i]}\n"
                i += 1
                continue

            operand_data = read_operands(definition, self.inst[i + 1 :])

            assert len(operand_data.operands) == len(definition.operand_widths)

            output += f"{i:04} {definition.name} "
            for operand in operand_data.operands:
                output += f"{operand}"

            output += "\n"

            i += 1 + operand_data.offset

        return output

    def add(self, instruction: list[int]) -> int:
        position = len(self.inst)
        self.inst.extend(instruction)
        return position

    def __getitem__(self, index: int) -> int:
        return self.inst[index]

    def __len__(self) -> int:
        return len(self.inst)

    def __iter__(self) -> Iterator[int]:
        return iter(self.inst)


@dataclass(frozen=True)
class OperandData:
    operands: list[int]
    offset: int


class OpCodes(IntEnum):
    OpConstant = auto()


@dataclass
class Definition:
    name: str
    operand_widths: list[int]


definitions: dict[Opcode, Definition] = {OpCodes.OpConstant: Definition("OpConstant", [2])}


def lookup(op: int) -> Definition | None:
    return definitions.get(op)


def make(op: Opcode, operands: list[int]) -> list[int]:
    definition = lookup(op)
    if definition is None:
        return []

    instruction = op.to_bytes()
    for i, operand in enumerate(operands):
        instruction += operand.to_bytes(definition.operand_widths[i], "big")
    return list(instruction)


def read_operands(definition: Definition, inst: list[int]) -> OperandData:
    operands: list[int] = []
    offset = 0

    for width in definition.operand_widths:
        operand = inst[offset : offset + width]
        operands.append(int.from_bytes(operand, "big"))
        offset += width

    return OperandData(operands=operands, offset=offset)
