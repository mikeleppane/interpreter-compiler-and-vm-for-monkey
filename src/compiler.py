from dataclasses import dataclass, field

from src.bytecode import Instructions, OpCodes, make
from src.libast import (
    ExpressionStatement,
    InfixExpression,
    IntegerLiteral,
    Node,
    Program,
)
from src.object import Integer, Object


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
            return
        if isinstance(node, ExpressionStatement):
            if node.expression is not None:
                self.compile(node.expression)
            return
        if isinstance(node, InfixExpression):
            self.compile(node.left)
            self.compile(node.right)
            match node.operator:
                case "+":
                    self.emit(OpCodes.OpAdd, [])
                # case "-":
                case _:
                    print(f"Error: unknown operator {node.operator}")
            return
        if isinstance(node, IntegerLiteral):
            integer = Integer(value=node.value)
            self.emit(OpCodes.OpConstant, [self.add_constant(integer)])
            return

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)

    def add_constant(self, obj: Object) -> int:
        self.constants.append(obj)
        return len(self.constants) - 1

    def emit(self, opcode: int, operands: list[int]) -> int:
        instruction = make(opcode, operands)
        return self.instructions.add(instruction)
