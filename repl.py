import getpass

from src.evaluator import eval
from src.lexer import Lexer
from src.libparser import Parser
from src.object import Environment, Null


class Repl:
    def run(self) -> None:
        env = Environment()
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
            evaluated = eval(program, env)
            if not isinstance(evaluated, Null):
                print(evaluated.inspect())

    def print_parser_errors(self, errors: list[str]) -> None:
        print("🐒")
        print("Woops! We ran into some monkey business here!")
        print("  parser errors:")
        for error in errors:
            print(f"\t{error}")


if __name__ == "__main__":
    print(f"Hello {getpass.getuser()}! This is the Monkey programming language!")
    print("Feel free to type in commands")
    repl = Repl()
    repl.run()
