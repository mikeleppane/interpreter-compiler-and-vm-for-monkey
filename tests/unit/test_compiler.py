import pytest

from src.bytecode import Instructions, OpCodes, make
from src.compiler import CompilationError, Compiler
from src.object import CompiledFunction, Object
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
        if isinstance(constant, list):
            assert isinstance(actual[index], CompiledFunction)
            verify_instructions(actual[index].instructions, flatten(constant))


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


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "[]",
            [],
            [
                make(OpCodes.OpArray, [0]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "[1, 2, 3]",
            [1, 2, 3],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpArray, [3]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "[1 + 2, 3 - 4, 5 * 6]",
            [1, 2, 3, 4, 5, 6],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpConstant, [3]),
                make(OpCodes.OpSub, []),
                make(OpCodes.OpConstant, [4]),
                make(OpCodes.OpConstant, [5]),
                make(OpCodes.OpMul, []),
                make(OpCodes.OpArray, [3]),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_array_literals(input, expected_constants, expected_instructions):
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
            "{}",
            [],
            [
                make(OpCodes.OpHash, [0]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "{1: 2, 3: 4, 5: 6}",
            [1, 2, 3, 4, 5, 6],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpConstant, [3]),
                make(OpCodes.OpConstant, [4]),
                make(OpCodes.OpConstant, [5]),
                make(OpCodes.OpHash, [6]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "{1: 2 + 3, 4: 5 * 6}",
            [1, 2, 3, 4, 5, 6],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpConstant, [3]),
                make(OpCodes.OpConstant, [4]),
                make(OpCodes.OpConstant, [5]),
                make(OpCodes.OpMul, []),
                make(OpCodes.OpHash, [4]),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_hash_literals(input, expected_constants, expected_instructions):
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
            "[1,2,3][1 + 1]",
            [1, 2, 3, 1, 1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpArray, [3]),
                make(OpCodes.OpConstant, [3]),
                make(OpCodes.OpConstant, [4]),
                make(OpCodes.OpAdd, []),
                make(OpCodes.OpIndex, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "{1: 2}[2 - 1]",
            [1, 2, 2, 1],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpHash, [2]),
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpConstant, [3]),
                make(OpCodes.OpSub, []),
                make(OpCodes.OpIndex, []),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_index_expressions(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)


def test_compiler_scopes():
    compiler = Compiler()
    assert compiler.scope_index == 0

    compiler.emit(OpCodes.OpMul, [])

    compiler.enter_scope()

    assert compiler.scope_index == 1

    compiler.emit(OpCodes.OpSub, [])

    assert len(compiler.scopes[compiler.scope_index].instructions) == 1

    last = compiler.scopes[compiler.scope_index].last_instruction

    assert last.opcode == OpCodes.OpSub

    compiler.leave_scope()

    assert compiler.scope_index == 0

    compiler.emit(OpCodes.OpAdd, [])

    assert len(compiler.scopes[compiler.scope_index].instructions) == 2

    last = compiler.scopes[compiler.scope_index].last_instruction

    assert last.opcode == OpCodes.OpAdd

    previous = compiler.scopes[compiler.scope_index].previous_instruction

    assert previous.opcode == OpCodes.OpMul


@pytest.mark.parametrize(
    "input,expected_constants,expected_instructions",
    [
        [
            "fn() { return 5 + 10 }",
            [
                5,
                10,
                [
                    make(OpCodes.OpConstant, [0]),
                    make(OpCodes.OpConstant, [1]),
                    make(OpCodes.OpAdd, []),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "fn() { 1; 2}",
            [
                1,
                2,
                [
                    make(OpCodes.OpConstant, [0]),
                    make(OpCodes.OpPop, []),
                    make(OpCodes.OpConstant, [1]),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "fn() { }",
            [
                [
                    make(OpCodes.OpReturn, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_functions(input, expected_constants, expected_instructions):
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
            "fn() { 24 }();",
            [
                24,
                [
                    make(OpCodes.OpConstant, [0]),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpCall, []),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "let noArg = fn() { 24 };noArg();",
            [
                24,
                [
                    make(OpCodes.OpConstant, [0]),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpSetGlobal, [0]),
                make(OpCodes.OpGetGlobal, [0]),
                make(OpCodes.OpCall, []),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_function_calls(input, expected_constants, expected_instructions):
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
            "let num = 55;fn() { num }",
            [
                55,
                [
                    make(OpCodes.OpGetGlobal, [0]),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [0]),
                make(OpCodes.OpSetGlobal, [0]),
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "fn() {let num = 55; num}",
            [
                55,
                [
                    make(OpCodes.OpConstant, [0]),
                    make(OpCodes.OpSetLocal, [0]),
                    make(OpCodes.OpGetLocal, [0]),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [1]),
                make(OpCodes.OpPop, []),
            ],
        ],
        [
            "fn() {let a = 55;let b = 77; a + b}",
            [
                55,
                77,
                [
                    make(OpCodes.OpConstant, [0]),
                    make(OpCodes.OpSetLocal, [0]),
                    make(OpCodes.OpConstant, [1]),
                    make(OpCodes.OpSetLocal, [1]),
                    make(OpCodes.OpGetLocal, [0]),
                    make(OpCodes.OpGetLocal, [1]),
                    make(OpCodes.OpAdd, []),
                    make(OpCodes.OpReturnValue, []),
                ],
            ],
            [
                make(OpCodes.OpConstant, [2]),
                make(OpCodes.OpPop, []),
            ],
        ],
    ],
)
def test_let_statement_scopes(input, expected_constants, expected_instructions):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)

    bytecode = compiler.bytecode()

    verify_instructions(bytecode.instructions, flatten(expected_instructions))

    verify_constants(bytecode.constants, expected_constants)
