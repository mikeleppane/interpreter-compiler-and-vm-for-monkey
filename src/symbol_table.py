from dataclasses import dataclass, field
from enum import StrEnum


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
    store: dict[str, Symbol] = field(default_factory=dict)
    num_definitions: int = 0

    def define(self, name: str) -> Symbol:
        symbol = Symbol(name=name, scope=SymbolScope.GLOBAL, index=self.num_definitions)
        self.store[name] = symbol
        self.num_definitions += 1
        return symbol

    def resolve(self, name: str) -> Symbol:
        try:
            return self.store[name]
        except KeyError:
            message = f"Symbol not defined: {name}"
            raise SymbolNotDefinedError(message) from None
