import pytest

from src.symbol_table import Symbol, SymbolNotDefinedError, SymbolScope, SymbolTable


def test_define():
    table = SymbolTable()
    table.define("a")
    table.define("b")

    assert table.store["a"] == Symbol(name="a", scope=SymbolScope.GLOBAL, index=0)
    assert table.store["b"] == Symbol(name="b", scope=SymbolScope.GLOBAL, index=1)


def test_resolve():
    table = SymbolTable()
    a = table.define("a")
    b = table.define("b")

    assert table.resolve("a") == a
    assert table.resolve("b") == b


def test_resolve_error():
    table = SymbolTable()
    a = table.define("a")
    b = table.define("b")

    with pytest.raises(SymbolNotDefinedError):
        table.resolve("c")
