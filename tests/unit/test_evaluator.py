import pytest

from src.evaluator import eval
from src.lexer import Lexer
from src.libparser import Parser
from src.object import Boolean, Integer, Object


def execute_eval(input: str) -> Object:
    lexer = Lexer(input)
    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    return eval(program)


def check_integer_object(obj: Object, expected: int):
    assert isinstance(obj, Integer)

    assert obj.value == expected


def check_boolean_object(obj: Object, expected: bool):
    assert isinstance(obj, Boolean)

    assert obj.value == expected


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
