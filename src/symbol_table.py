from dataclasses import dataclass, field
from enum import StrEnum
from typing import Self


class SymbolNotDefinedError(Exception):
    pass


class SymbolScope(StrEnum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"
    BUILTIN = "BUILTIN"
    FREE = "FREE"


@dataclass(frozen=True)
class Symbol:
    name: str
    scope: SymbolScope
    index: int


@dataclass
class SymbolTable:
    outer: Self | None = None
    store: dict[str, Symbol] = field(default_factory=dict)
    num_definitions: int = 0

    @classmethod
    def enclosed_by(cls, outer: Self) -> Self:
        return cls(outer=outer)

    def define(self, name: str) -> Symbol:
        if self.outer is None:
            symbol = Symbol(name=name, scope=SymbolScope.GLOBAL, index=self.num_definitions)
        else:
            symbol = Symbol(name=name, scope=SymbolScope.LOCAL, index=self.num_definitions)
        self.store[name] = symbol
        self.num_definitions += 1
        return symbol

    def resolve(self, name: str) -> Symbol | None:
        symbol = self.store.get(name)
        if symbol is None and self.outer is not None:
            return self.outer.resolve(name)
        return symbol
