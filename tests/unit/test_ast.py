from libast import FunctionLiteral, Identifier, LetStatement, Program, Statement
from tokens import Token, TokenType


def test_to_string():
    statements: list[Statement] = [
        LetStatement(
            token=Token(token_type=TokenType.LET, literal="let"),
            name=Identifier(
                token=Token(token_type=TokenType.IDENT, literal="myVar"), value="myVar"
            ),
            value=Identifier(
                token=Token(token_type=TokenType.IDENT, literal="anotherVar"),
                value="anotherVar",
            ),
        ),
    ]
    program = Program(statements=statements)

    assert program.to_string() == "let myVar = anotherVar;"
