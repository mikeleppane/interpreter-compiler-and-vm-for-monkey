import pytest

from src.bytecode import Instructions, OpCodes, lookup, make, read_operands
from tests.helper import flatten


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
        [
            make(OpCodes.OpConstant, [65535]),
            [OpCodes.OpConstant, 255, 255],
        ],
        [
            make(OpCodes.OpGetLocal, [255]),
            [OpCodes.OpGetLocal, 255],
        ],
    ],
)
def test_make(instructions: list[int], expected: list[int]) -> None:
    assert len(instructions) == len(expected)

    assert instructions == expected


def test_instruction_string():
    instructions: Instructions = Instructions(
        inst=flatten(
            [
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpGetLocal, [1]),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpConstant, [65535]),
            ]
        )
    )
    expected = """0000 OpAdd
                  0001 OpGetLocal 1
                  0003 OpConstant 2
                  0006 OpConstant 65535"""

    actual_lines = [
        line.strip() for line in instructions.to_string().split("\n") if line
    ]
    expected_lines = [line.strip() for line in expected.split("\n") if line]

    assert all(
        actual == expected
        for actual, expected in zip(actual_lines, expected_lines, strict=True)
    )


@pytest.mark.parametrize(
    "opcode,operands,bytes_read",
    [
        [
            OpCodes.OpConstant,
            [65535],
            2,
        ],
        [
            OpCodes.OpGetLocal,
            [255],
            1,
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
