import pytest

from src.evaluator import NULL, eval
from src.lexer import Lexer
from src.libparser import Parser
from src.object import (
    Array,
    Boolean,
    Environment,
    Error,
    Function,
    Hash,
    HashPair,
    Integer,
    Null,
    Object,
    String,
)


def execute_eval(input: str) -> Object:
    lexer = Lexer(input)
    parser = Parser(lexer=lexer)
    env = Environment()
    program = parser.parse_program()

    return eval(program, env)


def check_integer_object(obj: Object, expected: int):
    assert isinstance(obj, Integer)

    assert obj.value == expected


def check_string_object(obj: Object, expected: str):
    assert isinstance(obj, String)

    assert obj.value == expected


def check_boolean_object(obj: Object, expected: bool):
    assert isinstance(obj, Boolean)

    assert obj.value == expected


def check_null_object(obj: Object):
    assert obj == NULL


@pytest.mark.parametrize(
    "input,expected",
    [
        ["5", 5],
        ["10", 10],
        ["-5", -5],
        ["-10", -10],
        ["5 + 5 + 5 + 5 - 10", 10],
        ["2 * 2 * 2 * 2 * 2", 32],
        ["-50 + 100 + -50", 0],
        ["5 * 2 + 10", 20],
        ["5 + 2 * 10", 25],
        ["20 + 2 * -10", 0],
        ["50 / 2 * 2 + 10", 60],
        ["2 * (5 + 10)", 30],
        ["3 * 3 * 3 + 10", 37],
        ["3 * (3 * 3) + 10", 37],
        ["(5 + 10 * 2 + 15 / 3) * 2 + -10", 50],
    ],
)
def test_eval_integer_expression(input: str, expected: int):
    evaluated = execute_eval(input)
    check_integer_object(evaluated, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["!true", False],
        ["!false", True],
        ["!5", False],
        ["!!true", True],
        ["!!false", False],
        ["!!5", True],
    ],
)
def test_bang_operator(input: str, expected: bool):
    evaluated = execute_eval(input)
    check_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["true", True],
        ["false", False],
        ["1 < 2", True],
        ["1 > 2", False],
        ["1 < 1", False],
        ["1 > 1", False],
        ["1 == 1", True],
        ["1 != 1", False],
        ["1 == 2", False],
        ["1 != 2", True],
        ["true == true", True],
        ["false == false", True],
        ["true == false", False],
        ["true != false", True],
        ["false != true", True],
        ["(1 < 2) == true", True],
        ["(1 < 2) == false", False],
        ["(1 > 2) == true", False],
        ["(1 > 2) == false", True],
    ],
)
def test_eval_boolean_expression(input: str, expected: bool):
    evaluated = execute_eval(input)
    check_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["if (true) { 10 }", 10],
        ["if (false) { 10 }", None],
        ["if (1) { 10 }", 10],
        ["if (1 < 2) { 10 }", 10],
        ["if (1 > 2) { 10 }", None],
        ["if (1 > 2) { 10 } else { 20 }", 20],
        ["if (1 < 2) { 10 } else { 20 }", 10],
    ],
)
def test_if_else_expression(input: str, expected: int | None):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    else:
        check_null_object(evaluated)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["return 10;", 10],
        ["return 10; 9;", 10],
        ["return 2 * 5; 9;", 10],
        ["9; return 2 * 5; 9;", 10],
        [
            """
            if (10 > 1) {
                if (10 > 1) {
                    return 10;
                }
                return 1;
            }
            """,
            10,
        ],
    ],
)
def test_return_statements(input: str, expected: int | None):
    evaluated = execute_eval(input)
    print(evaluated)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    else:
        check_null_object(evaluated)


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            "5 + true;",
            "type mismatch: INTEGER + BOOLEAN",
        ],
        [
            "5 + true; 5;",
            "type mismatch: INTEGER + BOOLEAN",
        ],
        [
            "-true",
            "unknown operator: -BOOLEAN",
        ],
        [
            "true + false;",
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        [
            "5; true + false; 5",
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        [
            "if (10 > 1) { true + false; }",
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        [
            """
            if (10 > 1) {
                if (10 > 1) {
                    return true + false;
                }
                return 1;
            }
            """,
            "unknown operator: BOOLEAN + BOOLEAN",
        ],
        ["foobar", "identifier not found: foobar"],
        ['"Hello" - "World"', "unknown operator: STRING - STRING"],
        [
            '{"name": "Monkey"}[fn(x) { x }];',
            "unusable as hash key: FUNCTION",
        ],
    ],
)
def test_error_handling(input: str, expected: str):
    evaluated = execute_eval(input)
    assert isinstance(evaluated, Error)

    assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let a = 5; a;", 5],
        ["let a = 5 * 5; a;", 25],
        ["let a = 5; let b = a; b;", 5],
        ["let a = 5; let b = a; let c = a + b + 5; c;", 15],
    ],
)
def test_let_statements(input: str, expected: int):
    evaluated = execute_eval(input)
    check_integer_object(evaluated, expected)


def test_function_object():
    input = "fn(x) { x + 2; };"
    evaluated = execute_eval(input)

    assert isinstance(evaluated, Function)

    assert len(evaluated.parameters) == 1

    assert evaluated.parameters[0].value == "x"

    expected_body = "(x + 2)"

    assert evaluated.body.to_string() == expected_body


@pytest.mark.parametrize(
    "input,expected",
    [
        ["let identity = fn(x) { x; }; identity(5);", 5],
        ["let identity = fn(x) { return x; }; identity(5);", 5],
        ["let double = fn(x) { x * 2; }; double(5);", 10],
        ["let add = fn(x, y) { x + y; }; add(5, 5);", 10],
        ["let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20],
        ["fn(x) { x; }(5)", 5],
    ],
)
def test_function_application(input: str, expected: int):
    evaluated = execute_eval(input)
    check_integer_object(evaluated, expected)


def test_closures():
    input = """
        let newAdder = fn(x) {
            fn(y) { x + y };
        };
        let addTwo = newAdder(2);
        addTwo(2);
    """
    evaluated = execute_eval(input)
    check_integer_object(evaluated, 4)


def test_function_as_argument():
    input = """
        let add = fn(a, b) { a + b };
        let sub = fn(a, b) { a - b };
        let applyFunc = fn(a, b, func) { func(a, b) };
        applyFunc(2, 2, add);
    """
    evaluated = execute_eval(input)
    check_integer_object(evaluated, 4)


def test_string_literal():
    input = '"Hello World!"'

    evaluated = execute_eval(input)
    check_string_object(evaluated, "Hello World!")


def test_string_concatenation():
    input = '"Hello" + " " + "World!"'

    evaluated = execute_eval(input)
    check_string_object(evaluated, "Hello World!")


@pytest.mark.parametrize(
    "input,expected",
    [
        ['len("")', 0],
        ['len("four")', 4],
        ['len("hello world")', 11],
        ["len(1)", "argument to 'len' not supported, got INTEGER"],
        ['len("one", "two")', "wrong number of arguments. got=2, want=1"],
    ],
)
def test_len_builtin_functions(input: str, expected: int | str):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    if isinstance(expected, str):
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["first([1,2,3])", 1],
        ["first([0])", 0],
        ["first([])", Null],
        ["first(1)", "argument to 'first' must be ARRAY, got INTEGER"],
        ["first([1,2], [3,4])", "wrong number of arguments. got=2, want=1"],
    ],
)
def test_first_builtin_functions(input: str, expected: int | str):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    if isinstance(expected, Null):
        assert isinstance(evaluated, Null)
    if isinstance(expected, str):
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["last([1,2,3])", 3],
        ["last([0])", 0],
        ["last([])", Null],
        ["last(1)", "argument to 'last' must be ARRAY, got INTEGER"],
        ["last([1,2], [3,4])", "wrong number of arguments. got=2, want=1"],
    ],
)
def test_last_builtin_functions(input: str, expected: int | str):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    if isinstance(expected, Null):
        assert isinstance(evaluated, Null)
    if isinstance(expected, str):
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["rest([1,2,3])", [2, 3]],
        ["rest([1,2])", [2]],
        ["rest([])", Null],
        ["rest(1)", "argument to 'rest' must be ARRAY, got INTEGER"],
        ["rest([1,2], [3,4])", "wrong number of arguments. got=2, want=1"],
    ],
)
def test_rest_builtin_functions(input: str, expected: list | str):
    evaluated = execute_eval(input)
    if isinstance(expected, list):
        assert isinstance(evaluated, Array)
        assert len(evaluated.elements) == len(expected)
    if isinstance(expected, Null):
        assert isinstance(evaluated, Null)
    if isinstance(expected, str):
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["push([1,2,3], 1)", [1, 2, 3, 4]],
        ["push([], 1)", [1]],
        ["push(1,1)", "argument to 'push' must be ARRAY, got INTEGER"],
        ["push([1,2], [3,4], 1)", "wrong number of arguments. got=3, want=2"],
    ],
)
def test_push_builtin_functions(input: str, expected: list | str):
    evaluated = execute_eval(input)
    if isinstance(expected, list):
        assert isinstance(evaluated, Array)
        assert len(evaluated.elements) == len(expected)
    if isinstance(expected, Null):
        assert isinstance(evaluated, Null)
    if isinstance(expected, str):
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ['puts("Hello!")', "Hello!"],
    ],
)
def test_puts_builtin_functions(input: str, expected: list | str):
    evaluated = execute_eval(input)
    if isinstance(expected, str):
        assert isinstance(evaluated, Null)


def test_array_literals():
    input = "[1, 2 * 2, 3 + 3]"

    evaluated = execute_eval(input)

    assert isinstance(evaluated, Array)

    assert len(evaluated.elements) == 3

    check_integer_object(evaluated.elements[0], 1)
    check_integer_object(evaluated.elements[1], 4)
    check_integer_object(evaluated.elements[2], 6)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["[1,2,3][0]", 1],
        ["[1,2,3][1]", 2],
        ["[1,2,3][2]", 3],
        ["let i = 0; [1][i]", 1],
        ["[1, 2, 3][1 + 1];", 3],
        ["let myArray = [1, 2, 3]; myArray[2];", 3],
        ["let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6],
        ["let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2],
        ["[1, 2, 3][3]", None],
        ["[1, 2, 3][-1]", 3],
    ],
)
def test_array_index_expressions(input: str, expected: int | str):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    if expected is None:
        check_null_object(evaluated)


def test_map_function():
    input = """
        let map = fn(arr, f) {
            let iter = fn(arr, accumulated) {
                if (len(arr) == 0) {
                    accumulated
                } else {
                    iter(rest(arr), push(accumulated, f(first(arr))));
                }
            };
            iter(arr, []);
        };
        let a = [1,2,3,4];
        let double = fn(x) { x * 2};
        map(a, double)
"""
    evaluated = execute_eval(input)
    assert isinstance(evaluated, Array)
    assert len(evaluated.elements) == 4
    assert evaluated.elements[0].value == 2
    assert evaluated.elements[1].value == 4
    assert evaluated.elements[2].value == 6
    assert evaluated.elements[3].value == 8


def test_reduce_function():
    input = """
        let reduce = fn(arr, initial, f) {
                let iter = fn(arr, result) {
                    if (len(arr) == 0) {
                        result
                    } else {
                        iter(rest(arr), f(result, first(arr)));
                    }
                };
                    iter(arr, initial);
                };
        let sum = fn(arr) {
            reduce(arr, 0, fn(initial, el) { initial + el });
        };
        sum([1,2,3,4,5])
"""
    evaluated = execute_eval(input)
    assert isinstance(evaluated, Integer)
    assert evaluated.value == 15


def test_hash_literals():
    input = """
        let two = "two";
        {
            "one": 10 - 9,
            two: 1 + 1,
            "thr" + "ee": 6 / 2,
            4: 4,
            true: 5,
            false: 6
        }
"""
    evaluated = execute_eval(input)
    assert isinstance(evaluated, Hash)

    expected = {
        String("one"): 1,
        String("two"): 2,
        String("three"): 3,
        Integer(4): 4,
        Boolean(True): 5,
        Boolean(False): 6,
    }

    assert len(evaluated.pairs) == len(expected)
    for expected_key, expected_value in expected.items():
        pair = evaluated.pairs[expected_key]
        assert isinstance(pair, HashPair)
        check_integer_object(pair.value, expected_value)


@pytest.mark.parametrize(
    "input,expected",
    [
        ['{"foo": 5}["foo"]', 5],
        ['{"foo": 5}["bar"]', None],
        ['let key = "foo"; {"foo": 5}[key]', 5],
        ['{}["foo"]', None],
        ["{5: 5}[5]", 5],
        ["{true: 5}[true]", 5],
        ["{false: 5}[false]", 5],
        [
            'let people = [{"name": "Alice", "age": 24}, {"name": "Anna", "age": 28}];people[1]["age"] + people[0]["age"];',
            52,
        ],
        [
            'let getName = fn(person) { person["name"]; };let people = [{"name": "Alice", "age": 24}, {"name": "Anna", "age": 28}];people[1]["age"] + people[0]["age"];getName(people[0]);',
            "Alice",
        ],
    ],
)
def test_hash_index_expressions(input: str, expected: int | str | None):
    evaluated = execute_eval(input)
    if isinstance(expected, int):
        check_integer_object(evaluated, expected)
    if isinstance(expected, str):
        check_string_object(evaluated, expected)
    if expected is None:
        check_null_object(evaluated)
