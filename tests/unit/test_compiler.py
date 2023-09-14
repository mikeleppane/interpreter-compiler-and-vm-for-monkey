import pytest

from src.bytecode import Instructions, OpCodes, make
from src.compiler import CompilationError, Compiler
from src.object import Object
from tests.helper import flatten, parse, verify_integer_object, verify_string_object


def verify_instructions(actual: Instructions, expected: list[int]) -> None:
    assert len(actual.inst) == len(expected)

    for index, ins in enumerate(expected):
        assert actual[index] == ins


def verify_constants(actual: list[Object], expected: list[Object]) -> None:
    assert len(expected) == len(actual)

    for index, constant in enumerate(expected):
        if isinstance(constant, int):
            verify_integer_object(actual[index], constant)
        if isinstance(constant, str):
            verify_string_object(actual[index], constant)


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
        [
            "-1",
            [1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpMinus, []),
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


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "true",
            [],
            [
                make(OpCodes.OpTrue, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "false",
            [],
            [
                make(OpCodes.OpFalse, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1 > 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpGreaterThan, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1 < 2",
            [2, 1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpGreaterThan, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1 == 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpEqual, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "1 != 2",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpNotEqual, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "true == false",
            [],
            [
                make(OpCodes.OpTrue, []),
                make(OpCodes.OpFalse, []),
                make(OpCodes.OpEqual, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "true != false",
            [],
            [
                make(OpCodes.OpTrue, []),
                make(OpCodes.OpFalse, []),
                make(OpCodes.OpNotEqual, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "!true",
            [],
            [
                make(OpCodes.OpTrue, []),
                make(OpCodes.OpBang, []),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_boolean_expressions(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "if (true) { 10 }; 3333;",
            [10, 3333],
            [
                make(OpCodes.OpTrue, []),
                make(OpCodes.OpJumpNotTruthy, [10]),
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpJump, [11]),
                make(OpCodes.OpNull, []),
                make(OpCodes.OpPop, []),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "if (true) { 10 } else { 20 }; 3333;",
            [10, 20, 3333],
            [
                make(OpCodes.OpTrue, []),
                make(OpCodes.OpJumpNotTruthy, [10]),
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpJump, [13]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpPop, []),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_conditionals(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "let one = 1;let two = 2;",
            [1, 2],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpSetGlobal, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpSetGlobal, [1]),
            ],
        ],
        [
            "let one = 1;one",
            [1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpSetGlobal, [0]),
                make(OpCodes.OpGetGlobal, [0]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "let one = 1;let two = one; two",
            [1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpSetGlobal, [0]),
                make(OpCodes.OpGetGlobal, [0]),
                make(OpCodes.OpSetGlobal, [1]),
                make(OpCodes.OpGetGlobal, [1]),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_global_let_statements(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "let one = 1;two;",
            [1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpSetGlobal, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpSetGlobal, [1]),
            ],
        ],
    ],
)
def test_global_let_statements_compile_error(
    input, expected_constants, expected_instructions
):
    program = parse(input)
    compiler = Compiler()
    with pytest.raises(CompilationError):
        compiler.compile(program)


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            '"monkey"',
            ["monkey"],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            '"mon" + "key"',
            ["mon", "key"],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_string_expressions(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)
