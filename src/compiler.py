from dataclasses import dataclass, field

from src.bytecode import Instructions, OpCodes, make
from src.libast import (
    Boolean,
    ExpressionStatement,
    InfixExpression,
    IntegerLiteral,
    Node,
    Program,
)
from src.object import Integer, Object


class CompilationError(Exception):
    pass


@dataclass(frozen=True)
class Bytecode:
    instructions: Instructions
    constants: list[Object]


@dataclass(frozen=True)
class Compiler:
    instructions: Instructions = field(default_factory=Instructions)
    constants: list[Object] = field(default_factory=list)

    def compile(self, node: Node) -> None:
        if isinstance(node, Program):
            for statement in node.statements:
                self.compile(statement)
        if isinstance(node, InfixExpression):
            self.compile(node.left)
            self.compile(node.right)
            match node.operator:
                case "+":
                    self.emit(OpCodes.OpAdd, [])
                case "-":
                    self.emit(OpCodes.OpSub, [])
                case "*":
                    self.emit(OpCodes.OpMul, [])
                case "/":
                    self.emit(OpCodes.OpDiv, [])
                case _:
                    raise CompilationError(f"Error: unknown operator {node.operator}")
        if isinstance(node, IntegerLiteral):
            integer = Integer(value=node.value)
            self.emit(OpCodes.OpConstant, [self.add_constant(integer)])
        if isinstance(node, ExpressionStatement) and node.expression is not None:
            self.compile(node.expression)
            self.emit(OpCodes.OpPop, [])
        if isinstance(node, Boolean):
            if node.value:
                self.emit(OpCodes.OpTrue, [])
            else:
                self.emit(OpCodes.OpFalse, [])

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)

    def add_constant(self, obj: Object) -> int:
        self.constants.append(obj)
        return len(self.constants) - 1

    def emit(self, opcode: int, operands: list[int]) -> int:
        instruction = make(opcode, operands)
        return self.instructions.add(instruction)
