from dataclasses import dataclass, field
from typing import Self

from src.bytecode import Instructions, OpCodes
from src.compiler import Compiler
from src.object import Integer, Object

STACK_SIZE = 2048


class StackOverflow(Exception):
    pass


class StackUnderflow(Exception):
    pass


class EmptyStackObjectError(Exception):
    pass


@dataclass
class Stack:
    store: list[Object | None] = field(default_factory=list)
    stack_size: int = STACK_SIZE
    sp: int = 0

    def __post_init__(self) -> None:
        self.store = [None] * self.stack_size

    def last_popped_stack_elem(self) -> Object | None:
        return self.store[self.sp]

    def top(self) -> Object | None:
        if self.sp == 0:
            return None
        try:
            return self.store[self.sp - 1]
        except IndexError:
            print("Invalid stack index: {self.sp}, stack size: {len(self.stack)}")
            raise

    def push(self, obj: Object) -> None:
        if self.sp >= STACK_SIZE:
            raise StackOverflow(
                "Stack overflow: stack size is {STACK_SIZE}, stack pointer is {self.sp}"
            )
        self.store[self.sp] = obj
        self.sp += 1

    def pop(self) -> Object:
        if self.sp == 0:
            raise StackUnderflow("stack pointer cannot be negative")
        obj = self.store[self.sp - 1]
        if obj is None:
            raise EmptyStackObjectError("stack object cannot be None")
        self.sp -= 1
        return obj


@dataclass
class VM:
    constants: list[Object] = field(default_factory=list)
    instructions: Instructions = field(default_factory=Instructions)
    stack: Stack = field(default_factory=Stack)
    sp: int = 0

    def last_popped_stack_elem(self) -> Object | None:
        return self.stack.last_popped_stack_elem()

    def run(self) -> None:
        ip = 0
        while ip < len(self.instructions):
            opcode = OpCodes(self.instructions[ip])
            match opcode:
                case OpCodes.OpConstant:
                    const_index = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip += 2
                    self.push(self.constants[const_index])
                case OpCodes.OpAdd | OpCodes.OpSub | OpCodes.OpMul | OpCodes.OpDiv:
                    self.execute_binary_operation(opcode)
                case OpCodes.OpPop:
                    self.pop()
            ip += 1

    def push(self, obj: Object) -> None:
        return self.stack.push(obj)

    def pop(self) -> Object:
        return self.stack.pop()

    @classmethod
    def from_compiler(cls, compiler: Compiler) -> Self:
        return cls(
            instructions=compiler.bytecode().instructions,
            constants=compiler.bytecode().constants,
        )

    def execute_binary_operation(self, opcode: OpCodes) -> None:
        right = self.pop()
        left = self.pop()
        if not isinstance(left, Integer) or not isinstance(right, Integer):
            raise TypeError("operands must be integers")
        self.execute_integer_operation(opcode, left, right)

    def execute_integer_operation(self, opcode: OpCodes, left: Integer, right: Integer) -> None:
        match opcode:
            case OpCodes.OpAdd:
                self.push(Integer(value=left.value + right.value))
                return
            case OpCodes.OpSub:
                self.push(Integer(value=left.value - right.value))
                return
            case OpCodes.OpMul:
                self.push(Integer(value=left.value * right.value))
                return
            case OpCodes.OpDiv:
                self.push(Integer(value=left.value // right.value))
                return
            case _:
                raise TypeError("unknown integer operation: {opcode}")
