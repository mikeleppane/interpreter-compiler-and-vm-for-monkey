from collections import deque
from dataclasses import dataclass, field

from src.bytecode import Instructions, OpCodes
from src.object import Object

STACK_SIZE = 2048


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
            ip += 1

    def push(self, obj: Object) -> None:
        if self.sp >= STACK_SIZE:
            print("Stack overflow")
            return
        self.stack.append(obj)
        self.sp += 1
