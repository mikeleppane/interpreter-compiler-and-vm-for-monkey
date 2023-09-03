from src.libast import (
    BlockStatement,
    Boolean,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    Identifier,
    IfExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    Node,
    PrefixExpression,
    Program,
    ReturnStatement,
)
from src.object import OBJECT_TYPE
from src.object import Boolean as BooleanObject
from src.object import Environment, Error, Function, Integer, Null, Object, ReturnValue

NULL = Null()
TRUE = BooleanObject(value=True)
FALSE = BooleanObject(value=False)


def to_native_bool(value: bool) -> BooleanObject:
    if value:
        return TRUE
    return FALSE


def eval(node: Node | None, env: Environment) -> Object:  # noqa: C901
    if isinstance(node, Program):
        return eval_program(node, env)
    if isinstance(node, ExpressionStatement):
        return eval(node.expression, env)
    if isinstance(node, IntegerLiteral):
        return Integer(value=node.value)
    if isinstance(node, Boolean):
        if node.value:
            return TRUE
        return FALSE
    if isinstance(node, PrefixExpression):
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    if isinstance(node, InfixExpression):
        left = eval(node.left, env)
        right = eval(node.right, env)
        if is_error(left):
            return left
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    if isinstance(node, BlockStatement):
        return eval_block_statement(node, env)
    if isinstance(node, IfExpression):
        condition = eval(node.condition, env)
        if is_error(condition):
            return condition
        return eval_if_expression(node, env)
    if isinstance(node, ReturnStatement):
        val = eval(node.return_value, env)
        if is_error(val):
            return val
        return ReturnValue(value=val)
    if isinstance(node, LetStatement):
        val = eval(node.value, env)
        if is_error(val):
            return val
        env[node.name.value] = val
    if isinstance(node, Identifier):
        return eval_identifier(node, env)
    if isinstance(node, FunctionLiteral):
        params = node.parameters
        body = node.body
        return Function(parameters=params, body=body, env=env)
    if isinstance(node, CallExpression):
        func = eval(node.function, env)
        if is_error(func):
            return func
        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(func, args)

    return NULL


def apply_function(func: Object, args: list[Object]) -> Object:
    if not isinstance(func, Function):
        return Error(message=f"not a function: {func.type()}")
    extented_env = extend_function_env(func, args)
    evaluated = eval(func.body, extented_env)
    return unwrap_return_value(evaluated)


def unwrap_return_value(obj: Object) -> Object:
    if isinstance(obj, ReturnValue):
        return obj.value
    return obj


def extend_function_env(func: Function, args: list[Object]) -> Environment:
    env = Environment.create_enclosed_env(outer=func.env)
    for index, param in enumerate(func.parameters):
        env[param.value] = args[index]
    return env


def eval_expressions(exprs: list[Expression], env: Environment) -> list[Object]:
    result: list[Object] = []
    for expr in exprs:
        evaluated = eval(expr, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def eval_identifier(node: Identifier, env: Environment) -> Object:
    value = env[node.value]
    if value is not None:
        return value

    return Error(message=f"identifier not found: {node.value}")


def is_error(obj: Object | None) -> bool:
    if obj is not None:
        return obj.type() == OBJECT_TYPE.ERROR_OBJ
    return False


def eval_program(program: Program, env: Environment) -> Object:
    result: Object = NULL

    for stmt in program.statements:
        result = eval(stmt, env)
        if isinstance(result, ReturnValue):
            return result.value
        if isinstance(result, Error):
            return result

    return result


def eval_block_statement(block: BlockStatement, env: Environment) -> Object:
    result: Object = NULL

    for stmt in block.statements:
        result = eval(stmt, env)
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


def eval_if_expression(expr: IfExpression, env: Environment) -> Object:
    condition = eval(expr.condition, env)
    if is_truthy(condition):
        return eval(expr.consequence, env)
    if expr.alternative is not None:
        return eval(expr.alternative, env)
    return NULL


def is_truthy(obj: Object) -> bool:
    if obj == NULL:
        return False
    if obj == TRUE:
        return True
    if obj == FALSE:
        return False
    return True
