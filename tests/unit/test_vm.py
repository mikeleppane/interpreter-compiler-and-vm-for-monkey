from typing import Any

import pytest

from src.compiler import Compiler
from src.vm import VM
from tests.unit.helper import parse, verify_expected_object


def run_vm_test(input: str, expected: Any):
    program = parse(input)
    compiler = Compiler()
    compiler.compile(program)
    vm = VM(
        instructions=compiler.bytecode().instructions,
        constants=compiler.bytecode().constants,
    )
    vm.run()
    stack_elem = vm.last_popped_stack_elem()

    assert stack_elem is not None

    assert stack_elem is not None

    verify_expected_object(stack_elem, expected)


@pytest.mark.parametrize(
    "input,expected",
    [["1", 1], ["2", 2], ["1 + 2", 3]],
)
def test_integer_arithmetic(input: str, expected: Any) -> None:
    run_vm_test(input, expected)
