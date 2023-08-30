from src.libast import (
    Boolean,
    ExpressionStatement,
    IntegerLiteral,
    Node,
    Program,
    Statement,
)
from src.object import Boolean as BooleanObject
from src.object import Integer, Null, Object

NULL = Null()
TRUE = BooleanObject(value=True)
FALSE = BooleanObject(value=False)


def eval(node: Node | None) -> Object:
    if isinstance(node, Program):
        return eval_statements(node.statements)
    if isinstance(node, ExpressionStatement):
        return eval(node.expression)
    if isinstance(node, IntegerLiteral):
        return Integer(value=node.value)
    if isinstance(node, Boolean):
        if node.value:
            return TRUE
        return FALSE

    return NULL


def eval_statements(stmts: list[Statement]) -> Object:
    result: Object = NULL

    for stmt in stmts:
        result = eval(stmt)

    return result
