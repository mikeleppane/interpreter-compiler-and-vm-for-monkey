import pytest

from src.symbol_table import Symbol, SymbolNotDefinedError, SymbolScope, SymbolTable


def test_define():
    expected = {
        "a": Symbol(name="a", scope=SymbolScope.GLOBAL, index=0),
        "b": Symbol(name="b", scope=SymbolScope.GLOBAL, index=1),
        "c": Symbol(name="c", scope=SymbolScope.LOCAL, index=0),
        "d": Symbol(name="d", scope=SymbolScope.LOCAL, index=1),
        "e": Symbol(name="e", scope=SymbolScope.LOCAL, index=0),
        "f": Symbol(name="f", scope=SymbolScope.LOCAL, index=1),
    }

    st_global = SymbolTable()
    assert st_global.define("a") == expected["a"]
    assert st_global.define("b") == expected["b"]

    st_local = SymbolTable.enclosed_by(st_global)

    assert st_local.define("c") == expected["c"]
    assert st_local.define("d") == expected["d"]

    st_local = SymbolTable.enclosed_by(st_local)

    assert st_local.define("e") == expected["e"]
    assert st_local.define("f") == expected["f"]


def test_resolve_local():
    st_global = SymbolTable()
    st_global.define("a")
    st_global.define("b")

    st_local = SymbolTable.enclosed_by(st_global)
    st_local.define("c")
    st_local.define("d")

    expected = [
        Symbol(name="a", scope=SymbolScope.GLOBAL, index=0),
        Symbol(name="b", scope=SymbolScope.GLOBAL, index=1),
        Symbol(name="c", scope=SymbolScope.LOCAL, index=0),
        Symbol(name="d", scope=SymbolScope.LOCAL, index=1),
    ]

    for expected_symbol in expected:
        assert st_local.resolve(expected_symbol.name) == expected_symbol


def test_resolve_nested_local():
    st_global = SymbolTable()
    st_global.define("a")
    st_global.define("b")

    st_first_local = SymbolTable.enclosed_by(st_global)
    st_first_local.define("c")
    st_first_local.define("d")

    st_second_local = SymbolTable.enclosed_by(st_first_local)
    st_second_local.define("e")
    st_second_local.define("f")

    first_local_expected = [
        Symbol(name="a", scope=SymbolScope.GLOBAL, index=0),
        Symbol(name="b", scope=SymbolScope.GLOBAL, index=1),
        Symbol(name="c", scope=SymbolScope.LOCAL, index=0),
        Symbol(name="d", scope=SymbolScope.LOCAL, index=1),
    ]

    for expected_symbol in first_local_expected:
        assert st_first_local.resolve(expected_symbol.name) == expected_symbol

    second_local_expected = [
        Symbol(name="a", scope=SymbolScope.GLOBAL, index=0),
        Symbol(name="b", scope=SymbolScope.GLOBAL, index=1),
        Symbol(name="e", scope=SymbolScope.LOCAL, index=0),
        Symbol(name="f", scope=SymbolScope.LOCAL, index=1),
    ]

    for expected_symbol in second_local_expected:
        assert st_second_local.resolve(expected_symbol.name) == expected_symbol
