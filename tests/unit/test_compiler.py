import pytest

from src.bytecode import Instructions, OpCodes, make
from src.compiler import Compiler
from src.object import Object
from tests.unit.helper import flatten, parse, verify_integer_object


def verify_instructions(actual: Instructions, expected: list[int]) -> None:
    assert len(actual.inst) == len(expected)

    for index, ins in enumerate(expected):
        assert actual[index] == ins


def verify_constants(actual: list[Object], expected: list[Object]) -> None:
    assert len(expected) == len(actual)

    for index, constant in enumerate(expected):
        if isinstance(constant, int):
            verify_integer_object(actual[index], constant)


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "1 + 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1; 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpPop, []),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1 - 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpSub, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1 * 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpMul, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "2 / 1",
            [2, 1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpDiv, []),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_integer_arithmetic(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)
