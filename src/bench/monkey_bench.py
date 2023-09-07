import time

from src.evaluator import eval
from src.lexer import Lexer
from src.libparser import Parser
from src.object import Environment


def main():
    input = """
        let fibonacci = fn(x) {
                            if (x == 0) {
                                return 0;
                            } else {
                                if (x == 1) {
                                    return 1;
                                } else {
                                    return fibonacci(x - 1) + fibonacci(x - 2);
                                }
                            }
                        };
        fibonacci(35);
        """
    lexer = Lexer(input)
    parser = Parser(lexer=lexer)
    env = Environment()
    program = parser.parse_program()

    t1_start = time.perf_counter()
    eval(program, env)
    t1_stop = time.perf_counter()

    print(
        f"Fibonacci(35) in Monkey(tree-walking interpreter, host language Python): execution time in seconds: {t1_stop - t1_start}",
    )


if __name__ == "__main__":
    main()
