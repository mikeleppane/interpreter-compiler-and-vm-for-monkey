from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import TypeAlias

Opcode: TypeAlias = int


@dataclass
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

    def remove(self, position: int) -> None:
        self.inst = self.inst[:position]

    def replace(self, position: int, new_instructions: list[int]) -> None:
        self.inst[position : position + len(new_instructions)] = new_instructions

    def __getitem__(self, index: int) -> int:
        try:
            return self.inst[index]
        except IndexError:
            print(
                f"Index is out of bounds when trying to read instruction: given index {index}, instructions size: {len(self)}"
            )
            raise

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
    OpAdd = auto()
    OpPop = auto()
    OpSub = auto()
    OpMul = auto()
    OpDiv = auto()
    OpTrue = auto()
    OpFalse = auto()
    OpEqual = auto()
    OpNotEqual = auto()
    OpGreaterThan = auto()
    OpMinus = auto()
    OpBang = auto()
    OpJumpNotTruthy = auto()
    OpJump = auto()
    OpNull = auto()
    OpSetGlobal = auto()
    OpGetGlobal = auto()
    OpArray = auto()
    OpHash = auto()
    OpIndex = auto()
    OpCall = auto()
    OpReturnValue = auto()
    OpReturn = auto()
    OpGetLocal = auto()
    OpSetLocal = auto()


@dataclass(frozen=True)
class Definition:
    name: str
    operand_widths: list[int]


definitions: dict[Opcode, Definition] = {
    OpCodes.OpConstant: Definition("OpConstant", [2]),
    OpCodes.OpAdd: Definition("OpAdd", []),
    OpCodes.OpPop: Definition("OpPop", []),
    OpCodes.OpSub: Definition("OpSub", []),
    OpCodes.OpMul: Definition("OpMul", []),
    OpCodes.OpDiv: Definition("OpDiv", []),
    OpCodes.OpTrue: Definition("OpTrue", []),
    OpCodes.OpFalse: Definition("OpFalse", []),
    OpCodes.OpEqual: Definition("OpEqual", []),
    OpCodes.OpNotEqual: Definition("OpNotEqual", []),
    OpCodes.OpGreaterThan: Definition("OpGreaterThan", []),
    OpCodes.OpMinus: Definition("OpMinus", []),
    OpCodes.OpBang: Definition("OpBang", []),
    OpCodes.OpJumpNotTruthy: Definition("OpJumpNotTruthy", [2]),
    OpCodes.OpJump: Definition("OpJump", [2]),
    OpCodes.OpNull: Definition("OpNull", []),
    OpCodes.OpSetGlobal: Definition("OpSetGlobal", [2]),
    OpCodes.OpGetGlobal: Definition("OpGetGlobal", [2]),
    OpCodes.OpArray: Definition("OpArray", [2]),
    OpCodes.OpHash: Definition("OpHash", [2]),
    OpCodes.OpIndex: Definition("OpIndex", []),
    OpCodes.OpCall: Definition("OpCall", [1]),
    OpCodes.OpReturnValue: Definition("OpReturnValue", []),
    OpCodes.OpReturn: Definition("OpReturn", []),
    OpCodes.OpGetLocal: Definition("OpGetLocal", [1]),
    OpCodes.OpSetLocal: Definition("OpSetLocal", [1]),
}


def lookup(op: int) -> Definition | None:
    return definitions.get(op)


def make(op: Opcode, operands: list[int]) -> list[int]:
    definition = lookup(op)
    if definition is None:
        return []

    instruction = op.to_bytes()
    for i, operand in enumerate(operands):
        match definition.operand_widths[i]:
            case 2:
                instruction += operand.to_bytes(definition.operand_widths[i], "big")
            case 1:
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
