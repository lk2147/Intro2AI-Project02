import sys
import time
from pysat.solvers import Glucose4
from hashi_logic import Hashiwokakero 

class PySATSolver:
    def __init__(self, input_file):
        self.hashi = Hashiwokakero(input_file)
        self.solver = Glucose4()
        
    def solve(self):
        initial_cnfs = self.hashi.get_CNFs()
        for clause in initial_cnfs:
            self.solver.add_clause(clause)
        
        start_time = time.time()
        iteration = 0
        
        while True:
            iteration += 1
            is_sat = self.solver.solve()
            
            if is_sat:
                model = self.solver.get_model()
                cut_set = self.hashi.get_cut_set(model)
                
                if cut_set is None:
                    end_time = time.time()
                    print(f"Solution found after {iteration} iterations.")
                    print(f"Time: {end_time - start_time:.4f} seconds.")
                    self.hashi.print_solution(model)
                    return True
                else:
                    self.solver.add_clause(cut_set)
            else:
                print("\nNo solution.")
                return False
