from pysat.solvers import Glucose4
from BaseSolver import BaseSolver

class PySATSolver(BaseSolver):
    def __init__(self, fname):
        """
        Initialize SAT Solver and use Glucose4.
        """
        super().__init__(fname)
        self.nodes_expanded = 0 

    def solve(self):
        """
        Implement SAT Solver.
        """
        solver = Glucose4()
        for clause in self.cnfs:
            solver.add_clause(clause)  

        while True:
            is_sat = solver.solve()
            if not is_sat:
                return False
            
            model = solver.get_model()
            cut_set = self.hashi.get_cut_set(model) 
            if cut_set is None:
                self.solution = model
                return True
            
            solver.add_clause(cut_set)
            self.nodes_expanded += 1
