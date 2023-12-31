from dataclasses import dataclass, field
from typing import Self

from src.bytecode import Instructions, OpCodes, make
from src.libast import (
    ArrayLiteral,
    BlockStatement,
    Boolean,
    CallExpression,
    ExpressionStatement,
    FunctionLiteral,
    HashLiteral,
    Identifier,
    IfExpression,
    IndexExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    Node,
    PrefixExpression,
    Program,
    ReturnStatement,
    StringLiteral,
)
from src.object import CompiledFunction, Integer, Object, String
from src.symbol_table import SymbolScope, SymbolTable


class CompilationError(Exception):
    pass


@dataclass(frozen=True)
class Bytecode:
    instructions: Instructions
    constants: list[Object]


@dataclass
class EmittedInstruction:
    opcode: OpCodes | None = None
    position: int | None = None


@dataclass
class CompilationScope:
    instructions: Instructions = field(default_factory=Instructions)
    last_instruction: EmittedInstruction = field(default_factory=EmittedInstruction)
    previous_instruction: EmittedInstruction = field(default_factory=EmittedInstruction)

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


@dataclass
class Compiler:
    constants: list[Object] = field(default_factory=list)
    symbol_table: SymbolTable = field(default_factory=SymbolTable)
    scopes: list[CompilationScope] = field(default_factory=list)
    scope_index: int = 0

    def __post_init__(self) -> None:
        self.scopes.append(CompilationScope())

    @classmethod
    def with_new_state(cls, s: SymbolTable, constants: list[Object]) -> Self:
        return cls(symbol_table=s, constants=constants)

    def current_instructions(self) -> Instructions:
        return self.scopes[self.scope_index].instructions

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
            if self.is_last_instruction(OpCodes.OpPop):
                self.remove_last_pop()
            jump_pos = self.emit(OpCodes.OpJump, [9999])
            after_consequence_pos = len(self.current_instructions())
            self.change_operand(op_jump_not_truthy_pos, after_consequence_pos)
            if node.alternative is None:
                self.emit(OpCodes.OpNull, [])
            else:
                self.compile(node.alternative)
                if self.is_last_instruction(OpCodes.OpPop):
                    self.remove_last_pop()
            after_alternative_pos = len(self.current_instructions())
            self.change_operand(jump_pos, after_alternative_pos)
        if isinstance(node, BlockStatement):
            for statement in node.statements:
                self.compile(statement)
        if isinstance(node, LetStatement) and node.value is not None:
            self.compile(node.value)
            symbol = self.symbol_table.define(node.name.value)
            match symbol.scope:
                case SymbolScope.GLOBAL:
                    self.emit(OpCodes.OpSetGlobal, [symbol.index])
                case SymbolScope.LOCAL:
                    self.emit(OpCodes.OpSetLocal, [symbol.index])
        if isinstance(node, Identifier):
            maybe_symbol = self.symbol_table.resolve(node.value)
            if maybe_symbol is None:
                raise CompilationError(f"Error: identifier not found: {node.value}") from None
            match maybe_symbol.scope:
                case SymbolScope.GLOBAL:
                    self.emit(OpCodes.OpGetGlobal, [maybe_symbol.index])
                case SymbolScope.LOCAL:
                    self.emit(OpCodes.OpGetLocal, [maybe_symbol.index])
        if isinstance(node, StringLiteral):
            string = String(value=node.value)
            self.emit(OpCodes.OpConstant, [self.add_constant(string)])
        if isinstance(node, ArrayLiteral):
            for elem in node.elements:
                self.compile(elem)
            self.emit(OpCodes.OpArray, [len(node.elements)])
        if isinstance(node, HashLiteral):
            for key, value in node.pairs.items():
                self.compile(key)
                self.compile(value)
            self.emit(OpCodes.OpHash, [len(node.pairs) * 2])
        if isinstance(node, IndexExpression):
            self.compile(node.left)
            self.compile(node.index)
            self.emit(OpCodes.OpIndex, [])
        if isinstance(node, FunctionLiteral):
            self.enter_scope()

            for p in node.parameters:
                self.symbol_table.define(p.value)

            self.compile(node.body)

            if self.is_last_instruction(OpCodes.OpPop):
                self.replace_last_pop_with_return()

            if not self.is_last_instruction(OpCodes.OpReturnValue):
                self.emit(OpCodes.OpReturn, [])

            num_of_locals = self.symbol_table.num_definitions
            instructions = self.leave_scope()
            compiled_fn = CompiledFunction(
                instructions=instructions,
                num_of_locals=num_of_locals,
                num_of_parameters=len(node.parameters),
            )
            self.emit(opcode=OpCodes.OpConstant, operands=[self.add_constant(compiled_fn)])
        if isinstance(node, ReturnStatement) and node.return_value:
            self.compile(node.return_value)
            self.emit(OpCodes.OpReturnValue, [])
        if isinstance(node, CallExpression):
            self.compile(node.function)
            for arg in node.arguments:
                self.compile(arg)
            self.emit(OpCodes.OpCall, [len(node.arguments)])

    def bytecode(self) -> Bytecode:
        return Bytecode(
            instructions=self.current_instructions(),
            constants=self.constants,
        )

    def enter_scope(self) -> None:
        self.scopes.append(CompilationScope())
        self.scope_index += 1
        self.symbol_table = SymbolTable.enclosed_by(self.symbol_table)

    def leave_scope(self) -> Instructions:
        instructions = self.current_instructions()
        self.scopes.pop()
        self.scope_index -= 1
        if self.symbol_table.outer:
            self.symbol_table = self.symbol_table.outer
        return instructions

    def add_constant(self, obj: Object) -> int:
        self.constants.append(obj)
        return len(self.constants) - 1

    def emit(self, opcode: OpCodes, operands: list[int]) -> int:
        instruction = make(opcode, operands)
        pos = self.current_instructions().add(instruction)
        self.set_last_instruction(opcode, pos)
        return pos

    def set_last_instruction(self, opcode: OpCodes, position: int) -> None:
        self.scopes[self.scope_index].previous_instruction = self.scopes[
            self.scope_index
        ].last_instruction
        self.scopes[self.scope_index].last_instruction = EmittedInstruction(opcode, position)

    def is_last_instruction(self, op: OpCodes) -> bool:
        if len(self.current_instructions()) == 0:
            return False
        return self.scopes[self.scope_index].last_instruction.opcode == op

    def remove_last_pop(self) -> None:
        pos = self.scopes[self.scope_index].last_instruction.position
        if pos:
            self.current_instructions().remove(pos)
        self.scopes[self.scope_index].last_instruction = self.scopes[
            self.scope_index
        ].previous_instruction

    def change_operand(self, op_pos: int, operand: int) -> None:
        op = OpCodes(self.current_instructions()[op_pos])
        new_inst = make(op, [operand])
        self.current_instructions().replace(op_pos, new_inst)

    def replace_last_pop_with_return(self) -> None:
        last_pos = self.scopes[self.scope_index].last_instruction.position
        if last_pos is not None:
            self.current_instructions().replace(last_pos, make(OpCodes.OpReturnValue, []))
            self.scopes[self.scope_index].last_instruction.opcode = OpCodes.OpReturnValue
