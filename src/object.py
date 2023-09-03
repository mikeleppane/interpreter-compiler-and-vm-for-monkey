from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, Self, TypeAlias

from src.libast import BlockStatement, Identifier

ObjectType: TypeAlias = str


class OBJECT_TYPE(StrEnum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    RETURN_VALUE_OBJ = "RETURN_VALUE_OBJ"
    ERROR_OBJ = "ERROR_OBJ"
    FUNCTION_OBJ = "FUNCTION_OBJ"


class Object(Protocol):
    def type(self) -> ObjectType:
        ...

    def inspect(self) -> str:
        ...


@dataclass
class Integer(Object):
    value: int

    def type(self) -> ObjectType:
        return OBJECT_TYPE.INTEGER

    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool

    def type(self) -> ObjectType:
        return OBJECT_TYPE.BOOLEAN

    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Null(Object):
    def type(self) -> ObjectType:
        return OBJECT_TYPE.NULL

    def inspect(self) -> str:
        return "null"


@dataclass
class ReturnValue(Object):
    value: Object

    def type(self) -> ObjectType:
        return OBJECT_TYPE.RETURN_VALUE_OBJ

    def inspect(self) -> str:
        return self.value.inspect()


@dataclass
class Error(Object):
    message: str

    def type(self) -> ObjectType:
        return OBJECT_TYPE.ERROR_OBJ

    def inspect(self) -> str:
        return f"ERROR: {self.message}"

    @classmethod
    def build_error(cls, format: str) -> Self:
        return cls(message=format)


@dataclass
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
        env = cls()
        env.outer = outer
        return env


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
