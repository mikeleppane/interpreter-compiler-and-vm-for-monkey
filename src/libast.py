from dataclasses import dataclass, field
from typing import Protocol

from src.tokens import Token


class Node(Protocol):
    def token_literal(self) -> str:
        ...

    def to_string(self) -> str:
        ...


class Statement(Node, Protocol):
    def statement_node(self) -> None:
        ...


class Expression(Node, Protocol):
    def expression_node(self) -> None:
        ...


@dataclass
class Program(Node):
    statements: list[Statement] = field(default_factory=list)

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""

    def to_string(self) -> str:
        return "".join(stm.to_string() for stm in self.statements)


@dataclass
class Identifier(Expression):
    token: Token
    value: str

    def expression_node(self) -> None:
        return None

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return self.value


@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier
    value: Expression | None = None

    def statement_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return f"{self.token_literal()} {self.name.to_string()} = {self.value.to_string() if self.value else ''};"


@dataclass
class ReturnStatement(Statement):
    token: Token
    return_value: Expression | None = None

    def statement_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return (
            f"{self.token_literal()} {self.return_value.to_string() if self.return_value else ''};"
        )


@dataclass
class ExpressionStatement(Statement):
    token: Token
    expression: Expression | None = None

    def statement_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        if self.expression:
            return self.expression.to_string()
        return ""


@dataclass
class IntegerLiteral(Expression):
    token: Token
    value: int

    def expression_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return self.token.literal


@dataclass
class PrefixExpression(Expression):
    token: Token
    operator: str
    right: Expression

    def expression_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return f"({self.operator}{self.right.to_string()})"


@dataclass
class InfixExpression(Expression):
    token: Token
    left: Expression
    operator: str
    right: Expression

    def expression_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return f"({self.left.to_string()} {self.operator} {self.right.to_string()})"


@dataclass
class Boolean(Expression):
    token: Token
    value: bool

    def expression_node(self) -> None:
        ...

    def token_literal(self) -> str:
        return self.token.literal

    def to_string(self) -> str:
        return self.token.literal
