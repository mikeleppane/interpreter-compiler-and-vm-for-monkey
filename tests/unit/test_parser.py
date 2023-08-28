import pytest

from src.lexer import Lexer
from src.libast import (
    Boolean,
    ExpressionStatement,
    Identifier,
    IfExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    ReturnStatement,
)
from src.libparser import Parser


def check_parser_errors(parser: Parser):
    assert len(parser.errors) == 0


def check_boolean_literal():
    pass


def test_let_statements():
    input = """
    let x = 5;
    let y = 10;
    let foobar = 838383;
"""

    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 3
    check_parser_errors(parser=parser)

    expected_identifiers = ["x", "y", "foobar"]

    for i, ident in enumerate(expected_identifiers):
        statement = program.statements[i]

        assert statement.token_literal() == "let"
        assert isinstance(statement, LetStatement)
        assert statement.name.value == ident
        assert statement.name.token_literal() == ident


def test_let_statements_with_invalid_input():
    input = """
    let x 5;
    let = 10;
    let 838383;
"""

    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    parser.parse_program()

    with pytest.raises(AssertionError):
        check_parser_errors(parser=parser)
        assert len(parser.errors) == 3


def test_return_statements():
    input = """
    return 5;
    return 10;
    return 993322;
"""

    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 3
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ReturnStatement)
        assert statement.token_literal() == "return"


def test_identifier():
    input = "foobar;"

    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, Identifier)
        assert statement.expression.token_literal() == "foobar"
        assert statement.expression.value == "foobar"


def test_integer_literal_expression():
    input = "5;"

    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, IntegerLiteral)
        assert statement.expression.token_literal() == "5"
        assert statement.expression.value == 5


@pytest.mark.parametrize("input,operator,int_value", [["!5", "!", 5], ["-15", "-", 15]])
def test_parsing_prefix_expressions(input: str, operator: str, int_value: int):
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, PrefixExpression)
        assert statement.expression.operator == operator
        assert isinstance(statement.expression.right, IntegerLiteral)
        assert statement.expression.right.value == int_value
        assert statement.expression.right.token_literal() == str(int_value)


@pytest.mark.parametrize(
    "input,operator,boolean", [["!true", "!", True], ["!false", "!", False]]
)
def test_parsing_prefix_expressions_with_boolean(
    input: str, operator: str, boolean: bool
):
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)
        assert isinstance(statement.expression, PrefixExpression)
        assert statement.expression.operator == operator
        assert isinstance(statement.expression.right, Boolean)
        assert statement.expression.right.value == boolean
        assert statement.expression.right.token_literal() == str(boolean).lower()


@pytest.mark.parametrize(
    "input,left_value,operator,right_value",
    [
        ["5 + 5", 5, "+", 5],
        ["5 - 5;", 5, "-", 5],
        ["5 * 5;", 5, "*", 5],
        ["5 / 5;", 5, "/", 5],
        ["5 > 5;", 5, ">", 5],
        ["5 < 5;", 5, "<", 5],
        ["5 == 5;", 5, "==", 5],
        ["5 != 5;", 5, "!=", 5],
    ],
)
def test_parsing_infix_expressions_with_int(
    input: str, left_value: int | bool, operator: str, right_value: int | bool
):
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, InfixExpression)
        assert statement.expression.operator == operator

        assert isinstance(statement.expression.left, IntegerLiteral)
        assert statement.expression.left.value == left_value
        assert statement.expression.left.token_literal() == str(left_value)

        assert isinstance(statement.expression.right, IntegerLiteral)
        assert statement.expression.right.value == right_value
        assert statement.expression.right.token_literal() == str(right_value)


@pytest.mark.parametrize(
    "input,left_value,operator,right_value",
    [
        ["true == true", True, "==", True],
        ["true != false", True, "!=", False],
        ["false == false", False, "==", False],
    ],
)
def test_parsing_infix_expressions_with_bool(
    input: str, left_value: int | bool, operator: str, right_value: int | bool
):
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, InfixExpression)
        assert statement.expression.operator == operator

        assert isinstance(statement.expression.left, Boolean)
        assert statement.expression.left.value == left_value
        assert statement.expression.left.token_literal() == str(left_value).lower()

        assert isinstance(statement.expression.right, Boolean)
        assert statement.expression.right.value == right_value
        assert statement.expression.right.token_literal() == str(right_value).lower()


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "true",
            "true",
        ],
        [
            "false",
            "false",
        ],
        [
            "-a * b",
            "((-a) * b)",
        ],
        [
            "!-a",
            "(!(-a))",
        ],
        [
            "a + b + c",
            "((a + b) + c)",
        ],
        [
            "a + b - c",
            "((a + b) - c)",
        ],
        [
            "a * b * c",
            "((a * b) * c)",
        ],
        [
            "a * b / c",
            "((a * b) / c)",
        ],
        [
            "a + b / c",
            "(a + (b / c))",
        ],
        [
            "a + b * c + d / e - f",
            "(((a + (b * c)) + (d / e)) - f)",
        ],
        [
            "3 + 4; -5 * 5",
            "(3 + 4)((-5) * 5)",
        ],
        [
            "5 > 4 == 3 < 4",
            "((5 > 4) == (3 < 4))",
        ],
        [
            "5 < 4 != 3 > 4",
            "((5 < 4) != (3 > 4))",
        ],
        [
            "3 + 4 * 5 == 3 * 1 + 4 * 5",
            "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",
        ],
        [
            "1 + (2 + 3) + 4",
            "((1 + (2 + 3)) + 4)",
        ],
        [
            "(5 + 5) * 2",
            "((5 + 5) * 2)",
        ],
        [
            "2 / (5 + 5)",
            "(2 / (5 + 5))",
        ],
        [
            "-(5 + 5)",
            "(-(5 + 5))",
        ],
        [
            "!(true == true)",
            "(!(true == true))",
        ],
    ],
)
def test_operator_precedence_parsing(input: str, expected: str):
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    check_parser_errors(parser=parser)

    assert program.to_string() == expected


def test_if_expression():
    lexer = Lexer("if (x < y) { x }")

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, IfExpression)

        assert isinstance(statement.expression.condition, InfixExpression)
        assert statement.expression.condition.left.token_literal() == "x"
        assert statement.expression.condition.operator == "<"
        assert statement.expression.condition.right.token_literal() == "y"

        assert len(statement.expression.consequence.statements) == 1
        assert isinstance(
            statement.expression.consequence.statements[0], ExpressionStatement
        )
        assert (
            statement.expression.consequence.statements[0].expression.token_literal()
            == "x"
        )

        assert statement.expression.alternative is None


def test_if_else_expression():
    lexer = Lexer("if (x < y) { x } else {y}")

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, IfExpression)

        assert isinstance(statement.expression.condition, InfixExpression)
        assert statement.expression.condition.left.token_literal() == "x"
        assert statement.expression.condition.operator == "<"
        assert statement.expression.condition.right.token_literal() == "y"

        assert len(statement.expression.consequence.statements) == 1
        assert isinstance(
            statement.expression.consequence.statements[0], ExpressionStatement
        )
        assert (
            statement.expression.consequence.statements[0].expression.token_literal()
            == "x"
        )

        assert statement.expression.alternative is not None

        assert len(statement.expression.alternative.statements) == 1

        assert statement.expression.alternative.statements[0].token_literal() == "y"
