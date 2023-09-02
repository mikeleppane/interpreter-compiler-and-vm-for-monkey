from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, TypeAlias

ObjectType: TypeAlias = str


class OBJECT_TYPE(StrEnum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    RETURN_VALUE_OBJ = "RETURN_VALUE_OBJ"


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
