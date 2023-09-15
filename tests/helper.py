from itertools import chain
from typing import Any

from src.lexer import Lexer
from src.libast import Program
from src.libparser import Parser
from src.object import Array, Boolean, Integer, Object, String


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
    if isinstance(expected, str):
        verify_string_object(actual, expected)
        return
    if isinstance(expected, list):
        verify_list_object(actual, expected)
        return


def verify_list_object(actual: Object, expected: list) -> None:
    assert isinstance(actual, Array)

    assert len(actual.elements) == len(expected)

    for i, element in enumerate(actual.elements):
        verify_expected_object(element, expected[i])


def verify_boolean_object(actual: Object, expected: bool) -> None:
    assert isinstance(actual, Boolean)

    assert actual.value == expected


def verify_string_object(actual: Object, expected: str) -> None:
    assert isinstance(actual, String)

    assert actual.value == expected
