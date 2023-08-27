import getpass

from src.lexer import Lexer


class Repl:
    def run(self) -> None:
        while True:
            print(">> ", end="")
            line = input()
            if line == "exit" or not line:
                break
            lexer = Lexer(line)
            while True:
                token = lexer.next_token()
                if token.token_type == "EOF":
                    break
                print(token)


if __name__ == "__main__":
    print(f"Hello {getpass.getuser()}! This is the Monkey programming language!\n")
    print("Feel free to type in commands")
    repl = Repl()
    repl.run()
