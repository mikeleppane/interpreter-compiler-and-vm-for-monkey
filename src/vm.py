from collections import deque
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


@dataclass
class VM:
    constants: list[Object] = field(default_factory=list)
    instructions: Instructions = field(default_factory=Instructions)
    stack: deque[Object] = field(default_factory=deque)
    sp: int = 0

    def __post_init__(self) -> None:
        self.stack = deque(maxlen=STACK_SIZE)

    def stack_top(self) -> Object | None:
        if self.sp == 0:
            return None
        try:
            return self.stack[self.sp - 1]
        except IndexError:
            print("Invalid stack index: {self.sp}, stack size: {len(self.stack)}")
            raise

    def run(self) -> None:
        ip = 0
        while ip < len(self.instructions):
            opcode = OpCodes(self.instructions[ip])
            match opcode:
                case OpCodes.OpConstant:
                    const_index = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip += 2
                    self.push(self.constants[const_index])
                case OpCodes.OpAdd:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, Integer) and isinstance(right, Integer):
                        self.push(Integer(value=left.value + right.value))
            ip += 1

    def push(self, obj: Object) -> None:
        if self.sp >= STACK_SIZE:
            raise StackOverflow(
                "Stack overflow: stack size is {STACK_SIZE}, stack pointer is {self.sp}"
            )
        self.stack.append(obj)
        self.sp += 1

    def pop(self) -> Object:
        if self.sp == 0:
            raise StackUnderflow("stack pointer cannot be negative")
        self.sp -= 1
        return self.stack.pop()

    @classmethod
    def from_compiler(cls, compiler: Compiler) -> Self:
        return cls(
            instructions=compiler.bytecode().instructions,
            constants=compiler.bytecode().constants,
        )
