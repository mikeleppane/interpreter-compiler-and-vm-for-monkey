from dataclasses import dataclass, field
from typing import Self

from src.bytecode import Instructions, OpCodes, make
from src.libast import (
    BlockStatement,
    Boolean,
    ExpressionStatement,
    Identifier,
    IfExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    Node,
    PrefixExpression,
    Program,
    StringLiteral,
)
from src.object import Integer, Object, String
from src.symbol_table import SymbolNotDefinedError, SymbolTable


class CompilationError(Exception):
    pass


@dataclass(frozen=True)
class Bytecode:
    instructions: Instructions
    constants: list[Object]


@dataclass(frozen=True)
class EmittedInstruction:
    opcode: OpCodes | None = None
    position: int | None = None


@dataclass
class Compiler:
    instructions: Instructions = field(default_factory=Instructions)
    constants: list[Object] = field(default_factory=list)
    last_instruction: EmittedInstruction = field(default_factory=EmittedInstruction)
    previous_instruction: EmittedInstruction = field(default_factory=EmittedInstruction)
    symbol_table: SymbolTable = field(default_factory=SymbolTable)

    @classmethod
    def with_new_state(cls, s: SymbolTable, constants: list[Object]) -> Self:
        return cls(symbol_table=s, constants=constants)

    def compile(self, node: Node) -> None:  # noqa: C901
        if isinstance(node, Program):
            for statement in node.statements:
                self.compile(statement)
        if isinstance(node, InfixExpression):
            if node.operator == "<":
                self.compile(node.right)
                self.compile(node.left)
                self.emit(OpCodes.OpGreaterThan, [])
                return
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
                case ">":
                    self.emit(OpCodes.OpGreaterThan, [])
                case "==":
                    self.emit(OpCodes.OpEqual, [])
                case "!=":
                    self.emit(OpCodes.OpNotEqual, [])
                case _:
                    raise CompilationError(f"Error: unknown operator {node.operator}")
        if isinstance(node, PrefixExpression):
            self.compile(node.right)
            match node.operator:
                case "!":
                    self.emit(OpCodes.OpBang, [])
                case "-":
                    self.emit(OpCodes.OpMinus, [])
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
        if isinstance(node, IfExpression):
            self.compile(node.condition)
            op_jump_not_truthy_pos = self.emit(OpCodes.OpJumpNotTruthy, [9999])
            self.compile(node.consequence)
            if self.last_instruction.opcode == OpCodes.OpPop:
                self.remove_last_pop()
            jump_pos = self.emit(OpCodes.OpJump, [9999])
            after_consequence_pos = len(self.instructions)
            self.change_operand(op_jump_not_truthy_pos, after_consequence_pos)
            if node.alternative is None:
                self.emit(OpCodes.OpNull, [])
            else:
                self.compile(node.alternative)
                if self.last_instruction.opcode == OpCodes.OpPop:
                    self.remove_last_pop()
            after_alternative_pos = len(self.instructions)
            self.change_operand(jump_pos, after_alternative_pos)
        if isinstance(node, BlockStatement):
            for statement in node.statements:
                self.compile(statement)
        if isinstance(node, LetStatement) and node.value is not None:
            self.compile(node.value)
            symbol = self.symbol_table.define(node.name.value)
            self.emit(OpCodes.OpSetGlobal, [symbol.index])
        if isinstance(node, Identifier):
            try:
                symbol = self.symbol_table.resolve(node.value)
            except SymbolNotDefinedError:
                raise CompilationError(f"Error: identifier not found: {node.value}") from None
            self.emit(OpCodes.OpGetGlobal, [symbol.index])
        if isinstance(node, StringLiteral):
            string = String(value=node.value)
            self.emit(OpCodes.OpConstant, [self.add_constant(string)])

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)

    def add_constant(self, obj: Object) -> int:
        self.constants.append(obj)
        return len(self.constants) - 1

    def emit(self, opcode: OpCodes, operands: list[int]) -> int:
        instruction = make(opcode, operands)
        pos = self.instructions.add(instruction)
        self.set_last_instruction(opcode, pos)
        return pos

    def set_last_instruction(self, opcode: OpCodes, position: int) -> None:
        self.previous_instruction = self.last_instruction
        self.last_instruction = EmittedInstruction(opcode, position)

    def remove_last_pop(self) -> None:
        if self.last_instruction.position:
            self.instructions.remove(self.last_instruction.position)
        self.last_instruction = self.previous_instruction

    def change_operand(self, op_pos: int, operand: int) -> None:
        op = OpCodes(self.instructions[op_pos])
        new_inst = make(op, [operand])
        self.instructions.replace(op_pos, new_inst)
