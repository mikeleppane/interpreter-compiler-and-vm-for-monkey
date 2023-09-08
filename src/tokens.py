from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"
    IDENT = "IDENT"
    INT = "INT"
    ASSIGN = "="
    PLUS = "+"
    COMMA = ","
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"
    SEMICOLON = ";"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"
    LT = "<"
    GT = ">"
    EQ = "=="
    NOT_EQ = "!="
    STRING = "STRING"
    LBRACKET = "["
    RBRACKET = "]"


@dataclass
class Token:
    token_type: TokenType
    literal: str

    def has_token_type(self, token_type: TokenType) -> bool:
        return self.token_type == token_type


keywords = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
}


def lookup_ident(ident: str) -> TokenType:
    return keywords.get(ident, TokenType.IDENT)
