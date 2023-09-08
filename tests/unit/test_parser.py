import pytest

from src.lexer import Lexer
from src.libast import (
    ArrayLiteral,
    Boolean,
    CallExpression,
    ExpressionStatement,
    FunctionLiteral,
    Identifier,
    IfExpression,
    IndexExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    ReturnStatement,
    StringLiteral,
)
from src.libparser import Parser


def check_parser_errors(parser: Parser):
    assert len(parser.errors) == 0


def check_boolean_literal():
    pass


def test_let_statements():
    input = """
    let x = 5;
    let y = true;
    let foobar = y;
"""

    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 3
    check_parser_errors(parser=parser)

    expected_identifiers = ["x", "y", "foobar"]
    expected_values = [5, True, "y"]

    for i, ident in enumerate(expected_identifiers):
        statement = program.statements[i]

        assert isinstance(statement, LetStatement)
        assert statement.token_literal() == "let"
        assert statement.name.value == ident
        assert statement.value.value == expected_values[i]


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
        ["a + add(b * c) + d", "((a + add((b * c))) + d)"],
        [
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ],
        ["add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"],
        ["let x = 1 * 2 * 3 * 4 * 5", "let x = ((((1 * 2) * 3) * 4) * 5);"],
        ["x * y / 2 + 3 * 8 - 123", "((((x * y) / 2) + (3 * 8)) - 123)"],
        ["true == false", "(true == false)"],
        ["a * [1, 2, 3, 4][b * c] * d", "((a * ([1, 2, 3, 4][(b * c)])) * d)"],
        [
            "add(a * b[2], b[1], 2 * [1, 2][1])",
            "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
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


def test_function_literal_parsing():
    lexer = Lexer("fn(x, y) { x + y; }")

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, FunctionLiteral)

        assert len(statement.expression.parameters) == 2

        assert statement.expression.parameters[0].token_literal() == "x"
        assert statement.expression.parameters[1].token_literal() == "y"

        assert len(statement.expression.body.statements) == 1

        assert isinstance(statement.expression.body.statements[0], ExpressionStatement)

        assert isinstance(
            statement.expression.body.statements[0].expression, InfixExpression
        )

        assert (
            statement.expression.body.statements[0].expression.left.token_literal()
            == "x"
        )

        assert statement.expression.body.statements[0].expression.operator == "+"

        assert (
            statement.expression.body.statements[0].expression.right.token_literal()
            == "y"
        )


@pytest.mark.parametrize(
    "input,expected_params",
    [
        ["fn() {};", []],
        ["fn(x) {};", ["x"]],
        ["fn(x, y, z) {};", ["x", "y", "z"]],
    ],
)
def test_function_parameter_parsing(input: str, expected_params: list[str]):
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    check_parser_errors(parser=parser)

    assert isinstance(program.statements[0], ExpressionStatement)

    assert isinstance(program.statements[0].expression, FunctionLiteral)

    assert len(program.statements[0].expression.parameters) == len(expected_params)

    for i, param in enumerate(expected_params):
        assert program.statements[0].expression.parameters[i].token_literal() == param


def test_call_expression_parsing():
    lexer = Lexer("add(1, 2 * 3, 4 + 5);")

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, CallExpression)

        assert statement.expression.function.token_literal() == "add"

        assert len(statement.expression.arguments) == 3

        assert statement.expression.arguments[0].token_literal() == "1"

        assert isinstance(statement.expression.arguments[1], InfixExpression)

        assert statement.expression.arguments[1].left.token_literal() == "2"
        assert statement.expression.arguments[1].operator == "*"
        assert statement.expression.arguments[1].right.token_literal() == "3"

        assert isinstance(statement.expression.arguments[2], InfixExpression)

        assert statement.expression.arguments[2].left.token_literal() == "4"
        assert statement.expression.arguments[2].operator == "+"
        assert statement.expression.arguments[2].right.token_literal() == "5"


def test_string_literal_expression():
    lexer = Lexer('"hello world"')

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, StringLiteral)

        assert statement.expression.value == "hello world"


def test_parsing_array_literals():
    input = "[1, 2 * 2, 3 + 3]"
    lexer = Lexer(input)

    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, ArrayLiteral)

        assert len(statement.expression.elements) == 3

        assert isinstance(statement.expression.elements[0], IntegerLiteral)

        assert statement.expression.elements[0].value == 1

        assert isinstance(statement.expression.elements[1], InfixExpression)

        assert statement.expression.elements[1].left.value == 2

        assert statement.expression.elements[1].operator == "*"

        assert statement.expression.elements[1].right.value == 2

        assert isinstance(statement.expression.elements[2], InfixExpression)

        assert statement.expression.elements[2].left.value == 3

        assert statement.expression.elements[2].operator == "+"

        assert statement.expression.elements[2].right.value == 3


def test_parsing_index_expressions():
    input = "myArray[1 + 1]"

    lexer = Lexer(input)
    parser = Parser(lexer=lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    check_parser_errors(parser=parser)

    for statement in program.statements:
        assert isinstance(statement, ExpressionStatement)

        assert isinstance(statement.expression, IndexExpression)

        assert isinstance(statement.expression.left, Identifier)

        assert statement.expression.left.value == "myArray"

        assert isinstance(statement.expression.index, InfixExpression)

        assert statement.expression.index.left.value == 1

        assert statement.expression.index.operator == "+"

        assert statement.expression.index.right.value == 1
