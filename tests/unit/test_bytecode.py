import pytest

from src.bytecode import Instructions, OpCodes, lookup, make, read_operands
from tests.unit.helper import flatten


@pytest.mark.parametrize(
    "instructions,expected",
    [
        [
            make(OpCodes.OpConstant, [65534]),
            [OpCodes.OpConstant, 255, 254],
        ],
        [
            make(OpCodes.OpAdd, []),
            [OpCodes.OpAdd],
        ],
    ],
)
def test_make(instructions: list[int], expected: list[int]):
    assert len(instructions) == len(expected)

    assert instructions == expected


def test_instruction_string():
    instructions: Instructions = Instructions(
        inst=flatten(
            [
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpConstant, [65535]),
            ]
        )
    )
    expected = """0000 OpAdd 
0001 OpConstant 2
0004 OpConstant 65535"""

    print(instructions.to_string())
    print(expected)

    assert instructions.to_string().strip() == expected.strip()


@pytest.mark.parametrize(
    "opcode,operands,bytes_read",
    [
        [
            OpCodes.OpConstant,
            [65535],
            2,
        ],
    ],
)
def test_read_operands(opcode: int, operands: list[int], bytes_read: int) -> None:
    instructions: Instructions = Instructions(
        inst=make(opcode, operands),
    )
    definition = lookup(opcode)
    assert definition is not None

    operand_data = read_operands(definition, instructions.inst[1:])

    assert len(operand_data.operands) == len(operands)
    assert operand_data.offset == bytes_read

    for i, operand in enumerate(operands):
        assert operand_data.operands[i] == operand
