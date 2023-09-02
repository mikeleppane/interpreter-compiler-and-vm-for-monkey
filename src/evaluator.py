from src.libast import (
    BlockStatement,
    Boolean,
    ExpressionStatement,
    IfExpression,
    InfixExpression,
    IntegerLiteral,
    Node,
    PrefixExpression,
    Program,
    ReturnStatement,
)
from src.object import OBJECT_TYPE
from src.object import Boolean as BooleanObject
from src.object import Error, Integer, Null, Object, ReturnValue

NULL = Null()
TRUE = BooleanObject(value=True)
FALSE = BooleanObject(value=False)


def to_native_bool(value: bool) -> BooleanObject:
    if value:
        return TRUE
    return FALSE


def eval(node: Node | None) -> Object:  # noqa: C901
    if isinstance(node, Program):
        return eval_program(node)
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
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    if isinstance(node, InfixExpression):
        left = eval(node.left)
        right = eval(node.right)
        if is_error(left):
            return left
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    if isinstance(node, BlockStatement):
        return eval_block_statement(node)
    if isinstance(node, IfExpression):
        condition = eval(node.condition)
        if is_error(condition):
            return condition
        return eval_if_expression(node)
    if isinstance(node, ReturnStatement):
        val = eval(node.return_value)
        if is_error(val):
            return val
        return ReturnValue(value=val)

    return NULL


def is_error(obj: Object | None) -> bool:
    if obj is not None:
        return obj.type() == OBJECT_TYPE.ERROR_OBJ
    return False


def eval_program(program: Program) -> Object:
    result: Object = NULL

    for stmt in program.statements:
        result = eval(stmt)
        if isinstance(result, ReturnValue):
            return result.value
        if isinstance(result, Error):
            return result

    return result


def eval_block_statement(block: BlockStatement) -> Object:
    result: Object = NULL

    for stmt in block.statements:
        result = eval(stmt)
        if result != NULL:
            rt = result.type()
            if rt == OBJECT_TYPE.RETURN_VALUE_OBJ or rt == OBJECT_TYPE.ERROR_OBJ:
                return result

    return result


def eval_prefix_expression(operator: str, right: Object) -> Object:
    match operator:
        case "!":
            return eval_bang_operator_expression(right)
        case "-":
            return eval_minus_prefix_operator_expression(right)
        case _:
            return Error(message=f"unknown operator: {operator}{right.type()}")


def eval_bang_operator_expression(right: Object) -> Object:
    if right == TRUE:
        return FALSE
    if right == FALSE:
        return TRUE
    if right == NULL:
        return TRUE
    return FALSE


def eval_minus_prefix_operator_expression(right: Object) -> Object:
    if right.type() != OBJECT_TYPE.INTEGER:
        return Error(message=f"unknown operator: -{right.type()}")
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
        case _:
            if left.type() != right.type():
                return Error(message=f"type mismatch: {left.type()} {operator} {right.type()}")
            return Error(message=f"unknown operator: {left.type()} {operator} {right.type()}")


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
            return Error(message=f"unknown operator: {left.type()} {operator} {right.type()}")


def eval_if_expression(expr: IfExpression) -> Object:
    condition = eval(expr.condition)
    if is_truthy(condition):
        return eval(expr.consequence)
    if expr.alternative is not None:
        return eval(expr.alternative)
    return NULL


def is_truthy(obj: Object) -> bool:
    if obj == NULL:
        return False
    if obj == TRUE:
        return True
    if obj == FALSE:
        return False
    return True
