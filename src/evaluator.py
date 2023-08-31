from src.libast import (
    Boolean,
    ExpressionStatement,
    InfixExpression,
    IntegerLiteral,
    Node,
    PrefixExpression,
    Program,
    Statement,
)
from src.object import Boolean as BooleanObject
from src.object import Integer, Null, Object

NULL = Null()
TRUE = BooleanObject(value=True)
FALSE = BooleanObject(value=False)


def to_native_bool(value: bool) -> BooleanObject:
    if value:
        return TRUE
    return FALSE


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
    if isinstance(node, PrefixExpression):
        right = eval(node.right)
        return eval_prefix_expression(node.operator, right)
    if isinstance(node, InfixExpression):
        left = eval(node.left)
        right = eval(node.right)
        return eval_infix_expression(node.operator, left, right)

    return NULL


def eval_statements(stmts: list[Statement]) -> Object:
    result: Object = NULL

    for stmt in stmts:
        result = eval(stmt)

    return result


def eval_prefix_expression(operator: str, right: Object) -> Object:
    match operator:
        case "!":
            return eval_bang_operator_expression(right)
        case "-":
            return eval_minus_prefix_operator_expression(right)
        case _:
            return NULL


def eval_bang_operator_expression(right: Object) -> Object:
    if right == TRUE:
        return FALSE
    if right == FALSE:
        return TRUE
    if right == NULL:
        return TRUE
    return FALSE


def eval_minus_prefix_operator_expression(right: Object) -> Object:
    if not isinstance(right, Integer):
        return NULL

    value = right.value
    return Integer(value=-value)


def eval_infix_expression(operator: str, left: Object, right: Object) -> Object:
    if isinstance(left, Integer) and isinstance(right, Integer):
        return eval_integer_infix_expression(operator, left, right)
    match operator:
        case "==":
            return to_native_bool(value=left.value == right.value)  # type: ignore
        case "!=":
            return to_native_bool(value=left.value != right.value)  # type: ignore
    return NULL


def eval_integer_infix_expression(operator: str, left: Integer, right: Integer) -> Object:
    left_val = left.value
    right_val = right.value

    match operator:
        case "+":
            return Integer(value=left_val + right_val)
        case "-":
            return Integer(value=left_val - right_val)
        case "*":
            return Integer(value=left_val * right_val)
        case "/":
            return Integer(value=left_val // right_val)
        case "<":
            return to_native_bool(value=left_val < right_val)
        case ">":
            return to_native_bool(value=left_val > right_val)
        case "==":
            return to_native_bool(value=left_val == right_val)
        case "!=":
            return to_native_bool(value=left_val != right_val)
        case _:
            return NULL
