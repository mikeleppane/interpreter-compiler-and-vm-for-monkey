from typing import Any

import pytest

from src.compiler import Compiler
from src.object import Null
from src.vm import VM
from tests.helper import parse, verify_expected_object


def run_vm_test(input: str, expected: Any):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)
    vm = VM.from_compiler(compiler=compiler)
    vm.run()
    stack_elem = vm.last_popped_stack_elem()

    assert stack_elem is not None

    assert stack_elem is not None

    verify_expected_object(stack_elem, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["1", 1],
        ["2", 2],
        ["1 + 2", 3],
        ["1 - 2", -1],
        ["1 * 2", 2],
        ["4 / 2", 2],
        ["50 / 2 * 2 + 10 - 5", 55],
        ["5 + 5 + 5 + 5 - 10", 10],
        ["2 * 2 * 2 * 2 * 2", 32],
        ["5 * 2 + 10", 20],
        ["5 + 2 * 10", 25],
        ["5 * (2 + 10)", 60],
        ["-5", -5],
        ["-10", -10],
        ["-50 + 100 + -50", 0],
        ["(5 + 10 * 2 + 15 / 3) * 2 + -10", 50],
    ],
)
def test_integer_arithmetic(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["true", True],
        ["false", False],
        ["1 < 2", True],
        ["1 > 2", False],
        ["1 < 1", False],
        ["1 > 2", False],
        ["1 == 1", True],
        ["1 != 1", False],
        ["1 == 2", False],
        ["true == true", True],
        ["false == false", True],
        ["true == false", False],
        ["true != false", True],
        ["false != true", True],
        ["(1 < 2) == true", True],
        ["(1 < 2) == false", False],
        ["(1 > 2) == true", False],
        ["(1 > 2) == false", True],
        ["!true", False],
        ["!false", True],
        ["!5", False],
        ["!!true", True],
        ["!!false", False],
        ["!!5", True],
        ["(10 + 50 + -5 - 5 * 2 / 2) < (100 - 49)", True],
        ["!!true == false", False],
        ["!(if (false) { 5; })", True],
    ],
)
def test_boolean_expressions(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["if (true) { 10 }", 10],
        ["if (true) { 10 } else { 20 }", 10],
        ["if (false) { 10 } else { 20 } ", 20],
        ["if (1) { 10 }", 10],
        ["if (1 < 2) { 10 }", 10],
        ["if (1 < 2) { 10 } else { 20 }", 10],
        ["if ((if (false) { 10 })) { 10 } else { 20 }", 20],
    ],
)
def test_conditionals(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let one = 1; one", 1],
        ["let one = 1; let two = 2; one + two", 3],
        ["let one = 1; let two = one + one; one + two", 3],
        ["let one = 15; let two = one + one + one; let three = one + two + 5", 65],
    ],
)
def test_global_let_statements(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ['"monkey"', "monkey"],
        ['"mon" + "key"', "monkey"],
        ['"mon" + "key" + "banana"', "monkeybanana"],
    ],
)
def test_string_expressions(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["[]", []],
        ["[1, 2, 3]", [1, 2, 3]],
        ["[1 + 2, 3 * 4, 5 + 6]", [3, 12, 11]],
    ],
)
def test_array_literals(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["{}", {}],
        ["{1: 2, 2: 3}", {1: 2, 2: 3}],
        ["{1 + 1: 2 * 2, 3 + 3: 4 * 4}", {2: 4, 6: 16}],
    ],
)
def test_hash_literals(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["[1,2,3][1]", 2],
        ["[1,2,3][0 + 2]", 3],
        ["[[1,2,3]][0][0]", 1],
        ["[][0]", Null],
        ["[1,2,3][99]", Null],
        ["[1][-1]", Null],
        ["{1: 1, 2: 2}[1]", 1],
        ["{1: 1, 2: 2}[2]", 2],
        ["{1: 1}[0]", Null],
        ["{}[0]", Null],
    ],
)
def test_index_expressions(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let fivePlusTen = fn() { 5 + 10; }; fivePlusTen()", 15],
        ["let one = fn() { 1; };let two = fn() { 2; };one() + two()", 3],
        ["let a = fn() { 1 };let b = fn() { a() + 1 };let c = fn() { b() + 1 };c()", 3],
    ],
)
def test_calling_functions_without_arguments(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let earlyExit = fn() { return 99; 100; };earlyExit()", 99],
        ["let earlyExit = fn() { return 99; return 100; };earlyExit()", 99],
    ],
)
def test_functions_with_return_statements(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let noReturn = fn() { };noReturn();", Null],
        [
            "let noReturn = fn() { };let noReturnTwo = fn() { noReturn(); };noReturn();noReturnTwo();",
            Null,
        ],
    ],
)
def test_functions_without_return_value(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "let returnsOne = fn() { 1; };let returnsOneReturner = fn() { returnsOne; };returnsOneReturner()();",
            1,
        ],
        [
            "let returnsOneReturner = fn() { let returnsOne = fn() { 1; };returnsOne;};returnsOneReturner()();",
            1,
        ],
    ],
)
def test_first_class_functions(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "let one = fn() { let one = 1; one };one();",
            1,
        ],
        [
            "let oneAndTwo = fn() { let one = 1; let two = 2; one + two; };oneAndTwo();",
            3,
        ],
        [
            "let oneAndTwo = fn() { let one = 1; let two = 2; one + two; };let threeAndFour = fn() { let three = 3; let four = 4; three + four; };oneAndTwo() + threeAndFour();",
            10,
        ],
        [
            "let firstFoobar = fn() { let foobar = 50; foobar; };let secondFoobar = fn() { let foobar = 100; foobar; };firstFoobar() + secondFoobar();",
            150,
        ],
        [
            "let globalSeed = 50;let minusOne = fn() {let num = 1;globalSeed - num;}let minusTwo = fn() {let num = 2;globalSeed - num;}minusOne() + minusTwo();",
            97,
        ],
    ],
)
def test_calling_functions_with_bindings(input: str, expected: Any) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "let identity = fn(a) { a; };identity(4);",
            4,
        ],
        [
            "let sum = fn(a, b) { a + b; };sum(1, 2);",
            3,
        ],
        [
            "let sum = fn(a, b) {let c = a + b;c;};sum(1, 2);",
            3,
        ],
        [
            "let sum = fn(a, b) {let c = a + b;c;};sum(1, 2) + sum(3, 4);",
            10,
        ],
        [
            "let sum = fn(a, b) {let c = a + b;c;};let outer = fn() {sum(1, 2) + sum(3, 4);};outer();",
            10,
        ],
        [
            "let globalNum = 10;let sum = fn(a, b) {let c = a + b;c + globalNum;};let outer = fn() {sum(1, 2) + sum(3, 4) + globalNum;};outer() + globalNum;",
            50,
        ],
    ],
)
def test_calling_functions_with_arguments_and_bindings(
    input: str, expected: Any
) -> None:
    run_vm_test(input, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "fn() { 1; }(1);",
            "wrong number of arguments: want=0, got=1",
        ],
        [
            "fn(a) { a; }();",
            "wrong number of arguments: want=1, got=0",
        ],
        [
            "fn(a, b) { a + b; }(1);",
            "wrong number of arguments: want=2, got=1",
        ],
    ],
)
def test_calling_functions_with_wrong_arguments(input: str, expected: Any) -> None:
    with pytest.raises(RuntimeError) as excinfo:
        run_vm_test(input, expected)
    assert expected in str(excinfo.value)
