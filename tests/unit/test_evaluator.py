import pytest

from src.evaluator import eval
from src.lexer import Lexer
from src.libparser import Parser
from src.object import Integer, Null, Object


def execute_eval(input: str) -> Object:
    lexer = Lexer(input)
    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    return eval(program)


def check_integer_object(obj: Object, expected: int):
    assert isinstance(obj, Integer)

    assert obj.value == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["5", 5],
        ["10", 10],
    ],
)
def test_eval_integer_expression(input: str, expected: int):
    evaluated = execute_eval(input)
    check_integer_object(evaluated, expected)
