from lexer import Lexer
from tokens import TokenType


def test_next_token_with_simple_tokens():
    input = "=+(){},;"
    expected_tokens = [
        (TokenType.ASSIGN, "="),
        (TokenType.PLUS, "+"),
        (TokenType.LPAREN, "("),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.RBRACE, "}"),
        (TokenType.COMMA, ","),
        (TokenType.SEMICOLON, ";"),
        (TokenType.EOF, ""),
    ]
    lexer = Lexer(input)

    for expected_token in expected_tokens:
        token = lexer.next_token()

        assert token.token_type == expected_token[0]
        assert token.literal == expected_token[1]


def test_next_token_with_simple_code():
    input = """
    let five = 5;
    let ten = 10;

    let add = fn(x, y) {
        x + y;
    };

    let result = add(five, ten);
    !-/*5;
    5 < 10 > 5;

    if (5 < 10) {
        return true;
    } else {
        return false;
    }

    10 == 10;
    10 != 9;
"""
    expected_tokens = [
        (TokenType.LET, "let"),
        (TokenType.IDENT, "five"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "ten"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "add"),
        (TokenType.ASSIGN, "="),
        (TokenType.FUNCTION, "fn"),
        (TokenType.LPAREN, "("),
        (TokenType.IDENT, "x"),
        (TokenType.COMMA, ","),
        (TokenType.IDENT, "y"),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.IDENT, "x"),
        (TokenType.PLUS, "+"),
        (TokenType.IDENT, "y"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "result"),
        (TokenType.ASSIGN, "="),
        (TokenType.IDENT, "add"),
        (TokenType.LPAREN, "("),
        (TokenType.IDENT, "five"),
        (TokenType.COMMA, ","),
        (TokenType.IDENT, "ten"),
        (TokenType.RPAREN, ")"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.BANG, "!"),
        (TokenType.MINUS, "-"),
        (TokenType.SLASH, "/"),
        (TokenType.ASTERISK, "*"),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.INT, "5"),
        (TokenType.LT, "<"),
        (TokenType.INT, "10"),
        (TokenType.GT, ">"),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.IF, "if"),
        (TokenType.LPAREN, "("),
        (TokenType.INT, "5"),
        (TokenType.LT, "<"),
        (TokenType.INT, "10"),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.RETURN, "return"),
        (TokenType.TRUE, "true"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.ELSE, "else"),
        (TokenType.LBRACE, "{"),
        (TokenType.RETURN, "return"),
        (TokenType.FALSE, "false"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.INT, "10"),
        (TokenType.EQ, "=="),
        (TokenType.INT, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.INT, "10"),
        (TokenType.NOT_EQ, "!="),
        (TokenType.INT, "9"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.EOF, ""),
    ]
    lexer = Lexer(input)

    for expected_token in expected_tokens:
        token = lexer.next_token()

        assert token.token_type == expected_token[0]
        assert token.literal == expected_token[1]
