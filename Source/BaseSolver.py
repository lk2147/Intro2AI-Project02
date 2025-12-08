from abc import ABC, abstractmethod
from Hashi import Hashi

class BaseSolver(ABC):
    def __init__(self, fname):
        self.hashi = Hashi(fname)
        self.solution = []
    
    @abstractmethod
    def solve():
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def print_hashi(self):
        self.hashi.print_solution(self.solution)