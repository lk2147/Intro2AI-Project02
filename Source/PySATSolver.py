from pysat.solvers import Glucose4
from BaseSolver import BaseSolver

class PySATSolver(BaseSolver):
    def __init__(self, fname, max_iterations = 10):
        super().__init__(fname)
        self.max_iterations = max_iterations

    def solve(self):
        solver = Glucose4()
        for clause in self.cnfs:
            solver.add_clause(clause)  

        for _ in range(self.max_iterations):
            self.nodes_expanded += 1
            if solver.solve() == False:
                return False
            
            self.solution = solver.get_model()
            blocking_clause = self.hashi.get_cut_set(self.solution) 
            if blocking_clause is None:
                return True
            elif blocking_clause:
                solver.add_clause(blocking_clause)
            else:
                return False