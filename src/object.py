from collections.abc import Hashable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, Self, TypeAlias, runtime_checkable

from src.libast import BlockStatement, Identifier

ObjectType: TypeAlias = str


class OBJECT_TYPE(StrEnum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    RETURN_VALUE_OBJ = "RETURN_VALUE"
    ERROR_OBJ = "ERROR"
    FUNCTION_OBJ = "FUNCTION"
    STRING_OBJ = "STRING"
    BUILTIN_OBJ = "BUILTIN"
    ARRAY_OBJ = "ARRAY"
    HASH_OBJ = "HASH"


@runtime_checkable
class Object(Protocol):
    def type(self) -> ObjectType:
        ...

    def inspect(self) -> str:
        ...


@dataclass(frozen=True)
class Integer(Object, Hashable):
    value: int

    def type(self) -> ObjectType:
        return OBJECT_TYPE.INTEGER

    def inspect(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return super().__hash__()


@runtime_checkable
class BuiltinFunction(Protocol):
    def __call__(
        self,
        *args: Object,
    ) -> Object:
        ...


@dataclass(frozen=True)
class Boolean(Object, Hashable):
    value: bool

    def type(self) -> ObjectType:
        return OBJECT_TYPE.BOOLEAN

    def inspect(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class Null(Object):
    def type(self) -> ObjectType:
        return OBJECT_TYPE.NULL

    def inspect(self) -> str:
        return "null"

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class ReturnValue(Object):
    value: Object

    def type(self) -> ObjectType:
        return OBJECT_TYPE.RETURN_VALUE_OBJ

    def inspect(self) -> str:
        return self.value.inspect()

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class Error(Object):
    message: str

    def type(self) -> ObjectType:
        return OBJECT_TYPE.ERROR_OBJ

    def inspect(self) -> str:
        return f"ERROR: {self.message}"

    @classmethod
    def build_error(cls, format: str) -> Self:
        return cls(message=format)

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class Environment:
    store: dict[str, Object] = field(default_factory=dict)
    outer: Self | None = None

    def __getitem__(self, name: str) -> Object | None:
        obj = self.store.get(name)
        if obj is None and self.outer is not None:
            return self.outer[name]
        return obj

    def __setitem__(self, name: str, value: Object) -> Object:
        self.store[name] = value
        return value

    @classmethod
    def create_enclosed_env(cls, outer: Self) -> Self:
        return cls(outer=outer)

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class Function(Object):
    parameters: list[Identifier]
    body: BlockStatement
    env: Environment

    def type(self) -> ObjectType:
        return OBJECT_TYPE.FUNCTION_OBJ

    def inspect(self) -> str:
        params = [p.to_string() for p in self.parameters]
        return f"fn({', '.join(params)}) {{\n{self.body.to_string()}\n}}"


@dataclass(frozen=True)
class String(Object, Hashable):
    value: str

    def type(self) -> ObjectType:
        return OBJECT_TYPE.STRING_OBJ

    def inspect(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class Builtin(Object):
    fn: BuiltinFunction

    def type(self) -> ObjectType:
        return OBJECT_TYPE.BUILTIN_OBJ

    def inspect(self) -> str:
        return "builtin function"

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class Array(Object):
    elements: list[Object]

    def type(self) -> ObjectType:
        return OBJECT_TYPE.ARRAY_OBJ

    def inspect(self) -> str:
        elements = [e.inspect() for e in self.elements]
        return f"[{', '.join(elements)}]"

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(frozen=True)
class HashPair:
    key: Object
    value: Object


@dataclass(frozen=True)
class Hash(Object, Hashable):
    pairs: dict[Hashable, HashPair]

    def type(self) -> ObjectType:
        return OBJECT_TYPE.HASH_OBJ

    def inspect(self) -> str:
        pairs = [f"{pair.key.inspect()}: {pair.value.inspect()}" for pair in self.pairs.values()]
        return f"{{{', '.join(pairs)}}}"

    def __hash__(self) -> int:
        return super().__hash__()
