from dataclasses import dataclass, field
from typing import Self

from src.bytecode import Instructions, OpCodes
from src.compiler import Compiler
from src.object import Array, Boolean, Integer, Null, Object, String

STACK_SIZE = 2048
GLOBALS_SIZE = 65536


class StackOverflow(Exception):
    pass


class StackUnderflow(Exception):
    pass


class EmptyStackObjectError(Exception):
    pass


class GetGlobalIndexError(Exception):
    pass


TRUE = Boolean(value=True)
FALSE = Boolean(value=False)
NULL = Null()


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
class Globals:
    store: list[Object | None] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.store = [None] * GLOBALS_SIZE

    def __setitem__(self, index: int, obj: Object) -> None:
        self.store[index] = obj

    def __getitem__(self, index: int) -> Object | None:
        return self.store[index]


@dataclass
class VM:
    constants: list[Object] = field(default_factory=list)
    instructions: Instructions = field(default_factory=Instructions)
    stack: Stack = field(default_factory=Stack)
    globals: Globals = field(default_factory=Globals)

    @classmethod
    def with_new_state(cls, c: Compiler, globals: Globals) -> Self:
        vm = cls.from_compiler(compiler=c)
        vm.globals = globals
        return vm

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
                case OpCodes.OpTrue:
                    self.push(TRUE)
                case OpCodes.OpFalse:
                    self.push(FALSE)
                case OpCodes.OpEqual | OpCodes.OpNotEqual | OpCodes.OpGreaterThan:
                    self.execute_comparison(opcode)
                case OpCodes.OpBang:
                    self.execute_bang_operator()
                case OpCodes.OpMinus:
                    self.execute_minus_operator()
                case OpCodes.OpJump:
                    pos = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip = pos - 1
                case OpCodes.OpJumpNotTruthy:
                    pos = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip += 2
                    condition = self.pop()
                    if not self.is_truthy(condition):
                        ip = pos - 1
                case OpCodes.OpNull:
                    self.push(NULL)
                case OpCodes.OpSetGlobal:
                    global_index = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip += 2
                    self.globals[global_index] = self.pop()
                case OpCodes.OpGetGlobal:
                    global_index = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip += 2
                    obj = self.globals[global_index]
                    if obj is None:
                        raise GetGlobalIndexError(f"global at index {global_index} is None")
                    self.push(obj)
                case OpCodes.OpArray:
                    array_length = int.from_bytes(self.instructions.inst[ip + 1 : ip + 3], "big")
                    ip += 2
                    elements = self.stack.store[self.stack.sp - array_length : self.stack.sp]
                    if not all(elements):
                        raise EmptyStackObjectError(
                            f"array elements cannot be None: {elements} in range {self.stack.sp - array_length} to {self.stack.sp}"
                        )
                    array = Array(elements=elements)  # type: ignore[arg-type]
                    self.stack.sp -= array_length
                    self.push(array)

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
        if isinstance(left, Integer) and isinstance(right, Integer):
            self.execute_integer_operation(opcode, left, right)
            return
        if isinstance(left, String) and isinstance(right, String):
            self.execute_string_operation(opcode, left, right)
            return
        raise TypeError(f"unsupported types for binary operation: {left.type} {right.type}")

    def execute_string_operation(self, opcode: OpCodes, left: String, right: String) -> None:
        if opcode != OpCodes.OpAdd:
            raise TypeError(f"unknown string operation: {opcode}")
        self.push(String(value=left.value + right.value))

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

    def execute_comparison(self, opcode: OpCodes) -> None:
        right = self.pop()
        left = self.pop()
        if isinstance(left, Integer) and isinstance(right, Integer):
            self.execute_integer_comparison(opcode, left, right)
            return
        match opcode:
            case OpCodes.OpEqual:
                self.push(TRUE if left == right else FALSE)
            case OpCodes.OpNotEqual:
                self.push(TRUE if left != right else FALSE)
            case _:
                raise TypeError(f"unknown operator: {opcode} ({left.type} {right.type})")

    def execute_integer_comparison(self, opcode: OpCodes, left: Integer, right: Integer) -> None:
        match opcode:
            case OpCodes.OpEqual:
                self.push(TRUE if left.value == right.value else FALSE)
                return
            case OpCodes.OpNotEqual:
                self.push(TRUE if left.value != right.value else FALSE)
                return
            case OpCodes.OpGreaterThan:
                self.push(TRUE if left.value > right.value else FALSE)
                return
            case _:
                raise TypeError("unknown integer comparison: {opcode}")

    def execute_bang_operator(self) -> None:
        operand = self.pop()
        if operand in (FALSE, NULL):
            self.push(TRUE)
            return
        self.push(FALSE)

    def execute_minus_operator(self) -> None:
        operand = self.pop()
        if not isinstance(operand, Integer):
            raise TypeError(f"unsupported type for negation: {operand.type()}")
        self.push(Integer(value=-operand.value))

    def is_truthy(self, obj: Object) -> bool:
        if isinstance(obj, Boolean):
            return obj.value
        if obj is NULL:
            return False
        return True
