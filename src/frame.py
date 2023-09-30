from dataclasses import dataclass

from src.bytecode import Instructions
from src.object import CompiledFunction


@dataclass
class Frame:
    fn: CompiledFunction
    base_pointer: int
    ip: int = -1

    def instructions(self) -> Instructions:
        return self.fn.instructions
