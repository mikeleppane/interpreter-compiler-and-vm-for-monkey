from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import TypeAlias

from src.lexer import Lexer
from src.libast import (
    BlockStatement,
    Boolean,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    Identifier,
    IfExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
    Statement,
)
from src.tokens import Token, TokenType

PrefixParseFn: TypeAlias = Callable[[], Expression | None]
InfixParseFn: TypeAlias = Callable[[Expression], Expression | None]


class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()


precedences = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
}


@dataclass
class Parser:
    lexer: Lexer
    errors: list[str] = field(default_factory=list)
    current_token: Token = field(init=False)
    peek_token: Token = field(init=False)

    prefix_parse_fns: dict[TokenType, PrefixParseFn] = field(default_factory=dict)
    infix_parse_fns: dict[TokenType, InfixParseFn] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.peek_token: Token = self.lexer.next_token()
        self.next_token()
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_integer_literal)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.TRUE, self.parse_boolean)
        self.register_prefix(TokenType.FALSE, self.parse_boolean)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)
        self.register_prefix(TokenType.IF, self.parse_if_expression)
        self.register_prefix(TokenType.FUNCTION, self.parse_function_expression)
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)

    def next_token(self) -> None:
        self.current_token: Token = self.peek_token
        self.peek_token: Token = self.lexer.next_token()

    def parse_program(self) -> Program:
        program = Program()
        while not self.current_token.has_token_type(TokenType.EOF):
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)

            self.next_token()

        return program

    def parse_statement(self) -> Statement | None:
        match self.current_token.token_type:
            case TokenType.LET:
                return self.parse_let_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> LetStatement | None:
        current_token = self.current_token
        if not self.expect_peek(TokenType.IDENT):
            return None
        identifier = Identifier(token=self.current_token, value=self.current_token.literal)
        let_stm = LetStatement(token=current_token, name=identifier)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        while not self.current_token.has_token_type(TokenType.SEMICOLON):
            self.next_token()

        return let_stm

    def parse_return_statement(self) -> ReturnStatement:
        current_token = self.current_token
        self.next_token()

        while not self.current_token.has_token_type(TokenType.SEMICOLON):
            self.next_token()

        return ReturnStatement(token=current_token)

    def expect_peek(self, kind: TokenType) -> bool:
        if self.peek_token.has_token_type(kind):
            self.next_token()
            return True
        self.peek_error(token=kind)
        return False

    def peek_error(self, token: TokenType) -> None:
        message = f"expected next token to be {token}, got {self.peek_token.token_type} instead"
        self.errors.append(message)

    def register_prefix(self, token_type: TokenType, func: PrefixParseFn) -> None:
        self.prefix_parse_fns[token_type] = func

    def register_infix(self, token_type: TokenType, func: InfixParseFn) -> None:
        self.infix_parse_fns[token_type] = func

    def parse_expression_statement(self) -> ExpressionStatement:
        current_token = self.current_token

        expr = self.parse_expression(Precedence.LOWEST)
        stmt = ExpressionStatement(token=current_token, expression=expr)

        if self.peek_token.has_token_type(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_expression(self, precedence: int) -> Expression | None:
        prefix = self.prefix_parse_fns.get(self.current_token.token_type)
        if prefix is None:
            message = f"no prefix parse function for {self.current_token.token_type} found"
            self.errors.append(message)
            return None
        left_expr = prefix()

        while (
            not self.peek_token.has_token_type(TokenType.SEMICOLON)
            and precedence < self.peek_precedence()
        ):
            infix = self.infix_parse_fns.get(self.peek_token.token_type)
            if infix is None:
                return left_expr
            self.next_token()
            if left_expr:
                left_expr = infix(left_expr)
        return left_expr

    def parse_identifier(self) -> Expression:
        return Identifier(token=self.current_token, value=self.current_token.literal)

    def parse_integer_literal(self) -> Expression | None:
        try:
            value = int(self.current_token.literal)
        except ValueError:
            message = f"could not parse {self.current_token.literal} as integer"
            self.errors.append(message)
            return None
        return IntegerLiteral(token=self.current_token, value=value)

    def parse_prefix_expression(self) -> Expression | None:
        current_token = self.current_token

        self.next_token()

        right = self.parse_expression(Precedence.PREFIX)
        if right:
            return PrefixExpression(
                token=current_token, operator=current_token.literal, right=right
            )
        return None

    def peek_precedence(self) -> Precedence:
        precedence = precedences.get(self.peek_token.token_type)
        if precedence:
            return precedence
        return Precedence.LOWEST

    def current_precedence(self) -> Precedence:
        precedence = precedences.get(self.current_token.token_type)
        if precedence:
            return precedence
        return Precedence.LOWEST

    def parse_infix_expression(self, left: Expression) -> Expression | None:
        current_token = self.current_token
        precedence = self.current_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        if right:
            return InfixExpression(
                token=current_token,
                left=left,
                operator=current_token.literal,
                right=right,
            )
        return None

    def parse_boolean(self) -> Expression:
        return Boolean(
            token=self.current_token,
            value=self.current_token.has_token_type(TokenType.TRUE),
        )

    def parse_grouped_expression(self) -> Expression | None:
        self.next_token()

        expr = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return expr

    def parse_if_expression(self) -> Expression | None:
        current_token = self.current_token

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()
        condition = self.parse_expression(Precedence.LOWEST)
        if condition is None:
            return None

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        consequence = self.parse_block_statement()

        if_expr = IfExpression(token=current_token, condition=condition, consequence=consequence)

        if self.peek_token.has_token_type(TokenType.ELSE):
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None

            if_expr.alternative = self.parse_block_statement()

        return if_expr

    def parse_block_statement(self) -> BlockStatement:
        current_token = self.current_token
        statements: list[Statement] = []

        self.next_token()

        while not self.current_token.has_token_type(
            TokenType.RBRACE
        ) and not self.current_token.has_token_type(TokenType.EOF):
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            self.next_token()

        return BlockStatement(token=current_token, statements=statements)

    def parse_function_expression(self) -> Expression | None:
        current_token = self.current_token

        if not self.expect_peek(TokenType.LPAREN):
            return None

        parameters = self.parse_function_parameters()

        if not self.expect_peek(TokenType.LBRACE):
            return None

        body = self.parse_block_statement()

        return FunctionLiteral(token=current_token, parameters=parameters, body=body)

    def parse_function_parameters(self) -> list[Identifier]:
        identifiers: list[Identifier] = []

        if self.peek_token.has_token_type(TokenType.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        identifier = Identifier(token=self.current_token, value=self.current_token.literal)
        identifiers.append(identifier)

        while self.peek_token.has_token_type(TokenType.COMMA):
            self.next_token()
            self.next_token()
            identifier = Identifier(token=self.current_token, value=self.current_token.literal)
            identifiers.append(identifier)

        if not self.expect_peek(TokenType.RPAREN):
            return []

        return identifiers
