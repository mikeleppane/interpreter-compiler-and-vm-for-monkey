from dataclasses import dataclass

from src.tokens import Token, TokenType, lookup_ident


class UnrecognizedToken(Exception):
    pass


@dataclass
class Lexer:
    input: str
    position: int = 0
    read_position: int = 0
    current_char: str = ""

    def __post_init__(self) -> None:
        self.read_char()

    def read_char(self) -> None:
        if self.read_position >= len(self.input):
            self.current_char = ""
        else:
            self.current_char = self.input[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def next_token(self) -> Token:
        token = Token(token_type=TokenType.EOF, literal="")
        self.skip_whitespace()
        match self.current_char:
            case "=":
                if self.peek_char() == "=":
                    self.read_char()
                    token = Token(token_type=TokenType.EQ, literal="==")
                else:
                    token = Token(token_type=TokenType.ASSIGN, literal="=")
            case ";":
                token = Token(token_type=TokenType.SEMICOLON, literal=";")
            case "(":
                token = Token(token_type=TokenType.LPAREN, literal="(")
            case ")":
                token = Token(token_type=TokenType.RPAREN, literal=")")
            case ",":
                token = Token(token_type=TokenType.COMMA, literal=",")
            case "+":
                token = Token(token_type=TokenType.PLUS, literal="+")
            case "-":
                token = Token(token_type=TokenType.MINUS, literal="-")
            case "!":
                if self.peek_char() == "=":
                    self.read_char()
                    token = Token(token_type=TokenType.NOT_EQ, literal="!=")
                else:
                    token = Token(token_type=TokenType.BANG, literal="!")
            case "/":
                token = Token(token_type=TokenType.SLASH, literal="/")
            case "*":
                token = Token(token_type=TokenType.ASTERISK, literal="*")
            case "<":
                token = Token(token_type=TokenType.LT, literal="<")
            case ">":
                token = Token(token_type=TokenType.GT, literal=">")
            case "{":
                token = Token(token_type=TokenType.LBRACE, literal="{")
            case "}":
                token = Token(token_type=TokenType.RBRACE, literal="}")
            case "":
                token = token
            case _:
                if self._is_letter():
                    token.literal = self.read_identifier()
                    token.token_type = lookup_ident(token.literal)
                    return token
                if self.current_char.isdigit():
                    token.token_type = TokenType.INT
                    token.literal = self.read_number()
                    return token
                token = Token(token_type=TokenType.ILLEGAL, literal=self.current_char)
        self.read_char()
        return token

    def read_identifier(self) -> str:
        position = self.position
        while self._is_letter():
            self.read_char()
        return self.input[position : self.position]

    def _is_letter(self) -> bool:
        return self.current_char.isalpha() or self.current_char == "_"

    def skip_whitespace(self) -> None:
        while self.current_char.isspace():
            self.read_char()

    def read_number(self) -> str:
        position = self.position
        while self.current_char.isdigit():
            self.read_char()
        return self.input[position : self.position]

    def peek_char(self) -> str:
        if self.read_position >= len(self.input):
            return ""
        return self.input[self.read_position]
