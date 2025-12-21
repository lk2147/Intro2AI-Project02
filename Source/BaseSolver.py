from abc import ABC, abstractmethod
from Hashi import Hashi

class BaseSolver(ABC):
    def __init__(self, fname):
        self.hashi = Hashi(fname)
        self.num_variables = self.hashi.get_number_of_variables()
        self.cnfs = self.hashi.get_CNFs()
        self.solution = None

        # Metrics
        self.time_elapsed = 0.0
        self.memory_peak = 0.0
        self.nodes_expanded = 0 

    @abstractmethod
    def solve():
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def print_hashi(self):
        self.hashi.print_solution(self.solution)