from src.libast import ExpressionStatement, IntegerLiteral, Node, Program, Statement
from src.object import Integer, Null, Object


def eval(node: Node | None) -> Object:
    if isinstance(node, Program):
        return eval_statements(node.statements)
    if isinstance(node, ExpressionStatement):
        return eval(node.expression)
    if isinstance(node, IntegerLiteral):
        return Integer(value=node.value)

    return Null()


def eval_statements(stmts: list[Statement]) -> Object:
    result: Object = Null()

    for stmt in stmts:
        result = eval(stmt)

    return result
