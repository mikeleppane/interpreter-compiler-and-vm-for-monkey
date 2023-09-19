from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Self

from src.bytecode import OpCodes
from src.compiler import Compiler
from src.frame import Frame
from src.object import (
    Array,
    Boolean,
    CompiledFunction,
    Hash,
    HashPair,
    Integer,
    Null,
    Object,
    String,
)

STACK_SIZE = 2048
GLOBALS_SIZE = 65536
MAX_FRAMES = 1024


class VmError(Exception):
    pass


class StackOverflow(VmError):
    pass


class StackUnderflow(VmError):
    pass


class EmptyStackObjectError(VmError):
    pass


class EmptyFrameError(VmError):
    pass


class InvalidHashKeyError(VmError):
    pass


class GetGlobalIndexError(VmError):
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
    stack: Stack = field(default_factory=Stack)
    globals: Globals = field(default_factory=Globals)
    frames: list[Frame | None] = field(default_factory=list)
    frame_index: int = 0

    def current_frame(self) -> Frame:
        frame = self.frames[self.frame_index - 1]
        if frame is not None:
            return frame
        raise EmptyFrameError("Frame cannot be None")

    def push_frame(self, frame: Frame) -> None:
        self.frames[self.frame_index] = frame
        self.frame_index += 1

    def pop_frame(self) -> Frame:
        self.frame_index -= 1
        frame = self.frames[self.frame_index]
        if frame is not None:
            return frame
        raise EmptyFrameError("Frame cannot be None")

    @classmethod
    def with_new_state(cls, c: Compiler, globals: Globals) -> Self:
        vm = cls.from_compiler(compiler=c)
        vm.globals = globals
        return vm

    def last_popped_stack_elem(self) -> Object | None:
        return self.stack.last_popped_stack_elem()

    def run(self) -> None:  # noqa: C901
        ip = 0
        while self.current_frame().ip < len(self.current_frame().instructions()) - 1:
            self.current_frame().ip += 1
            ip = self.current_frame().ip
            ins = self.current_frame().instructions().inst
            opcode = OpCodes(ins[ip])
            match opcode:
                case OpCodes.OpConstant:
                    const_index = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip += 2
                    self.stack.push(self.constants[const_index])
                case OpCodes.OpAdd | OpCodes.OpSub | OpCodes.OpMul | OpCodes.OpDiv:
                    self.execute_binary_operation(opcode)
                case OpCodes.OpPop:
                    self.stack.pop()
                case OpCodes.OpTrue:
                    self.stack.push(TRUE)
                case OpCodes.OpFalse:
                    self.stack.push(FALSE)
                case OpCodes.OpEqual | OpCodes.OpNotEqual | OpCodes.OpGreaterThan:
                    self.execute_comparison(opcode)
                case OpCodes.OpBang:
                    self.execute_bang_operator()
                case OpCodes.OpMinus:
                    self.execute_minus_operator()
                case OpCodes.OpJump:
                    pos = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip = pos - 1
                case OpCodes.OpJumpNotTruthy:
                    pos = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip += 2
                    condition = self.stack.pop()
                    if not self.is_truthy(condition):
                        self.current_frame().ip = pos - 1
                case OpCodes.OpNull:
                    self.stack.push(NULL)
                case OpCodes.OpSetGlobal:
                    global_index = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip += 2
                    self.globals[global_index] = self.stack.pop()
                case OpCodes.OpGetGlobal:
                    global_index = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip += 2
                    obj = self.globals[global_index]
                    if obj is None:
                        raise GetGlobalIndexError(f"global at index {global_index} is None")
                    self.stack.push(obj)
                case OpCodes.OpArray:
                    array_length = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip += 2
                    elements = self.stack.store[self.stack.sp - array_length : self.stack.sp]
                    if not all(elements):
                        raise EmptyStackObjectError(
                            f"array elements cannot be None: {elements} in range {self.stack.sp - array_length} to {self.stack.sp}"
                        )
                    array = Array(elements=elements)  # type: ignore[arg-type]
                    self.stack.sp -= array_length
                    self.stack.push(array)
                case OpCodes.OpHash:
                    hash_length = int.from_bytes(ins[ip + 1 : ip + 3], "big")
                    self.current_frame().ip += 2
                    pairs: dict[Hashable, HashPair] = {}
                    for i in range(self.stack.sp - hash_length, self.stack.sp, 2):
                        key = self.stack.store[i]
                        value = self.stack.store[i + 1]
                        if (
                            isinstance(key, Object)
                            and isinstance(key, Hashable)
                            and value is not None
                        ):
                            pairs[key] = HashPair(key=key, value=value)
                        else:
                            raise InvalidHashKeyError(f"unsupported hash key: {key}")
                    self.stack.sp -= hash_length
                    self.stack.push(Hash(pairs=pairs))
                case OpCodes.OpIndex:
                    index = self.stack.pop()
                    left = self.stack.pop()
                    if isinstance(left, Array) and isinstance(index, Integer):
                        self.execute_array_index(left, index)
                    elif isinstance(left, Hash):
                        self.execute_hash_index(left, index)
                    else:
                        raise TypeError(f"index operator not supported: {left.type()}")
                case OpCodes.OpCall:
                    fn = self.stack.store[self.stack.sp - 1]
                    if not isinstance(fn, CompiledFunction):
                        raise AssertionError("calling non-function")
                    self.push_frame(Frame(fn=fn))
                case OpCodes.OpReturnValue:
                    rv = self.stack.pop()
                    self.pop_frame()
                    self.stack.pop()
                    self.stack.push(rv)
                case OpCodes.OpReturn:
                    self.pop_frame()
                    self.stack.pop()
                    self.stack.push(NULL)

            ip += 1

    def execute_array_index(self, left: Array, index: Integer) -> None:
        if index.value < 0 or index.value >= len(left.elements):
            self.stack.push(NULL)
            return
        self.stack.push(left.elements[index.value])

    def execute_hash_index(self, left: Hash, index: Object) -> None:
        if not isinstance(index, Hashable):
            raise InvalidHashKeyError(f"unusable as hash key: {index.type()}")
        pair = left.pairs.get(index)
        if pair is None:
            self.stack.push(NULL)
            return
        self.stack.push(pair.value)

    @classmethod
    def from_compiler(cls, compiler: Compiler) -> Self:
        main_fn = CompiledFunction(instructions=compiler.bytecode().instructions)
        main_frame = Frame(
            fn=main_fn,
        )
        frames: list[Frame | None] = [None] * MAX_FRAMES
        frames[0] = main_frame
        return cls(constants=compiler.bytecode().constants, frames=frames, frame_index=1)

    def execute_binary_operation(self, opcode: OpCodes) -> None:
        right = self.stack.pop()
        left = self.stack.pop()
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
        self.stack.push(String(value=left.value + right.value))

    def execute_integer_operation(self, opcode: OpCodes, left: Integer, right: Integer) -> None:
        match opcode:
            case OpCodes.OpAdd:
                self.stack.push(Integer(value=left.value + right.value))
                return
            case OpCodes.OpSub:
                self.stack.push(Integer(value=left.value - right.value))
                return
            case OpCodes.OpMul:
                self.stack.push(Integer(value=left.value * right.value))
                return
            case OpCodes.OpDiv:
                self.stack.push(Integer(value=left.value // right.value))
                return
            case _:
                raise TypeError("unknown integer operation: {opcode}")

    def execute_comparison(self, opcode: OpCodes) -> None:
        right = self.stack.pop()
        left = self.stack.pop()
        if isinstance(left, Integer) and isinstance(right, Integer):
            self.execute_integer_comparison(opcode, left, right)
            return
        match opcode:
            case OpCodes.OpEqual:
                self.stack.push(TRUE if left == right else FALSE)
            case OpCodes.OpNotEqual:
                self.stack.push(TRUE if left != right else FALSE)
            case _:
                raise TypeError(f"unknown operator: {opcode} ({left.type} {right.type})")

    def execute_integer_comparison(self, opcode: OpCodes, left: Integer, right: Integer) -> None:
        match opcode:
            case OpCodes.OpEqual:
                self.stack.push(TRUE if left.value == right.value else FALSE)
                return
            case OpCodes.OpNotEqual:
                self.stack.push(TRUE if left.value != right.value else FALSE)
                return
            case OpCodes.OpGreaterThan:
                self.stack.push(TRUE if left.value > right.value else FALSE)
                return
            case _:
                raise TypeError("unknown integer comparison: {opcode}")

    def execute_bang_operator(self) -> None:
        operand = self.stack.pop()
        if operand in (FALSE, NULL):
            self.stack.push(TRUE)
            return
        self.stack.push(FALSE)

    def execute_minus_operator(self) -> None:
        operand = self.stack.pop()
        if not isinstance(operand, Integer):
            raise TypeError(f"unsupported type for negation: {operand.type()}")
        self.stack.push(Integer(value=-operand.value))

    def is_truthy(self, obj: Object) -> bool:
        if isinstance(obj, Boolean):
            return obj.value
        if obj is NULL:
            return False
        return True
