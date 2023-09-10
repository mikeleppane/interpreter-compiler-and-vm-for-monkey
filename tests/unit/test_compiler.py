import pytest

from src.bytecode import Instructions, OpCodes, make
from src.compiler import Compiler
from src.lexer import Lexer
from src.libast import Program
from src.libparser import Parser
from src.object import Integer, Object
from tests.unit.helper import flatten


def parse(input: str) -> Program:
    return Parser(lexer=Lexer(input=input)).parse_program()


def verify_instructions(actual: Instructions, expected: list[int]) -> None:
    assert len(actual.inst) == len(expected)

    for index, ins in enumerate(expected):
        assert actual[index] == ins


def verify_integer_object(actual: Object, expected: int) -> None:
    assert isinstance(actual, Integer)

    assert actual.value == expected


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
            [make(OpCodes.OpConstant, [0]), make(OpCodes.OpConstant, [1])],
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
