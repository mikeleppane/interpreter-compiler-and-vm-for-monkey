import getpass

from src.compiler import CompilationError, Compiler, SymbolTable
from src.lexer import Lexer
from src.libparser import Parser
from src.object import Environment, Object
from src.vm import VM, Globals

"""
# to use tree-walking interpreter:
evaluated = eval(program, env)
if not isinstance(evaluated, Null):
print(evaluated.inspect())

"""


class Repl:
    def run(self) -> None:
        Environment()
        constants: list[Object] = []
        globals = Globals()
        symbol_table = SymbolTable()

        while True:
            print(">> ", end="")
            line = input()
            if line == "exit" or not line:
                break
            lexer = Lexer(line)
            parser = Parser(lexer)
            program = parser.parse_program()
            if len(parser.errors) > 0:
                self.print_parser_errors(parser.errors)
                continue
            compiler = Compiler.with_new_state(symbol_table, constants)
            try:
                compiler.compile(program)
            except CompilationError as e:
                print("Woops! Compilation failed:")
                print(e)
                continue
            machine = VM.with_new_state(compiler, globals)
            machine.run()

            stack_top = machine.last_popped_stack_elem()
            print(stack_top.inspect() if stack_top is not None else "null")

    def print_parser_errors(self, errors: list[str]) -> None:
        print("🐒")
        print("Woops! We ran into some monkey business here!")
        print("  parser errors:")
        for error in errors:
            print(f"\t{error}")


def main() -> None:
    print(f"Hello {getpass.getuser()}! This is the Monkey programming language!")
    print("Feel free to type in commands")
    repl = Repl()
    repl.run()


if __name__ == "__main__":
    main()
