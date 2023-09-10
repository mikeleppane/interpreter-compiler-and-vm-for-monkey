from dataclasses import dataclass, field

from src.bytecode import Instructions
from src.libast import Node
from src.object import Object


@dataclass
class Bytecode:
    instructions: Instructions
    constants: list[Object]


@dataclass
class Compiler:
    instructions: Instructions = field(default_factory=Instructions)
    constants: list[Object] = field(default_factory=list)

    def compile(self, node: Node) -> None:
        return None

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)
