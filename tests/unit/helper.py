from itertools import chain
from typing import Any

from src.lexer import Lexer
from src.libast import Program
from src.libparser import Parser
from src.object import Boolean, Integer, Object


def flatten(to_be_flatten: list[list[int]]) -> list[int]:
    return list(chain.from_iterable(to_be_flatten))


def parse(input: str) -> Program:
    return Parser(lexer=Lexer(input=input)).parse_program()


def verify_integer_object(actual: Object, expected: int) -> None:
    assert isinstance(actual, Integer)

    assert actual.value == expected


def verify_expected_object(actual: Object, expected: Any) -> None:
    if isinstance(expected, bool):
        verify_boolean_object(actual, expected)
        return
    if isinstance(expected, int):
        verify_integer_object(actual, expected)
        return


def verify_boolean_object(actual: Object, expected: bool) -> None:
    assert isinstance(actual, Boolean)

    assert actual.value == expected
