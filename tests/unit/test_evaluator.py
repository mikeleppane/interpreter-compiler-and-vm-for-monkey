import pytest

from src.evaluator import NULL, eval
from src.lexer import Lexer
from src.libparser import Parser
from src.object import Boolean, Environment, Error, Integer, Object


def execute_eval(input: str) -> Object:
    lexer = Lexer(input)
    parser = Parser(lexer=lexer)
    env = Environment()
    program = parser.parse_program()

    return eval(program, env)


def check_integer_object(obj: Object, expected: int):
    assert isinstance(obj, Integer)

    assert obj.value == expected


def check_boolean_object(obj: Object, expected: bool):
    assert isinstance(obj, Boolean)

    assert obj.value == expected


def check_null_object(obj: Object):
    assert obj == NULL


@pytest.mark.parametrize(
    "input,expected",
    [
        ["5", 5],
        ["10", 10],
        ["-5", -5],
        ["-10", -10],
        ["5 + 5 + 5 + 5 - 10", 10],
        ["2 * 2 * 2 * 2 * 2", 32],
        ["-50 + 100 + -50", 0],
        ["5 * 2 + 10", 20],
        ["5 + 2 * 10", 25],
        ["20 + 2 * -10", 0],
        ["50 / 2 * 2 + 10", 60],
        ["2 * (5 + 10)", 30],
        ["3 * 3 * 3 + 10", 37],
        ["3 * (3 * 3) + 10", 37],
        ["(5 + 10 * 2 + 15 / 3) * 2 + -10", 50],
    ],
)
def test_eval_integer_expression(input: str, expected: int):
    evaluated = execute_eval(input)
    check_integer_object(evaluated, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["!true", False],
        ["!false", True],
        ["!5", False],
        ["!!true", True],
        ["!!false", False],
        ["!!5", True],
    ],
)
def test_bang_operator(input: str, expected: bool):
    evaluated = execute_eval(input)
    check_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["true", True],
        ["false", False],
        ["1 < 2", True],
        ["1 > 2", False],
        ["1 < 1", False],
        ["1 > 1", False],
        ["1 == 1", True],
        ["1 != 1", False],
        ["1 == 2", False],
        ["1 != 2", True],
        ["true == true", True],
        ["false == false", True],
        ["true == false", False],
        ["true != false", True],
        ["false != true", True],
        ["(1 < 2) == true", True],
        ["(1 < 2) == false", False],
        ["(1 > 2) == true", False],
        ["(1 > 2) == false", True],
    ],
)
def test_eval_boolean_expression(input: str, expected: bool):
    evaluated = execute_eval(input)
    check_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["if (true) { 10 }", 10],
        ["if (false) { 10 }", None],
        ["if (1) { 10 }", 10],
        ["if (1 < 2) { 10 }", 10],
        ["if (1 > 2) { 10 }", None],
        ["if (1 > 2) { 10 } else { 20 }", 20],
        ["if (1 < 2) { 10 } else { 20 }", 10],
    ],
)
def test_if_else_expression(input: str, expected: int | None):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    else:
        check_null_object(evaluated)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["return 10;", 10],
        ["return 10; 9;", 10],
        ["return 2 * 5; 9;", 10],
        ["9; return 2 * 5; 9;", 10],
        [
            """
            if (10 > 1) {
                if (10 > 1) {
                    return 10;
                }
                return 1;
            }
            """,
            10,
        ],
    ],
)
def test_return_statements(input: str, expected: int | None):
    evaluated = execute_eval(input)
    print(evaluated)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    else:
        check_null_object(evaluated)


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "5 + true;",
            "type mismatch: INTEGER + BOOLEAN",
        ],
        [
            "5 + true; 5;",
            "type mismatch: INTEGER + BOOLEAN",
        ],
        [
            "-true",
            "unknown operator: -BOOLEAN",
        ],
        [
            "true + false;",
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        [
            "5; true + false; 5",
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        [
            "if (10 > 1) { true + false; }",
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        [
            """
            if (10 > 1) {
                if (10 > 1) {
                    return true + false;
                }
                return 1;
            }
            """,
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        ["foobar", "identifier not found: foobar"],
    ],
)
def test_error_handling(input: str, expected: str):
    evaluated = execute_eval(input)
    assert isinstance(evaluated, Error)

    assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let a = 5; a;", 5],
        ["let a = 5 * 5; a;", 25],
        ["let a = 5; let b = a; b;", 5],
        ["let a = 5; let b = a; let c = a + b + 5; c;", 15],
    ],
)
def test_let_statements(input: str, expected: int):
    evaluated = execute_eval(input)
    check_integer_object(evaluated, expected)
