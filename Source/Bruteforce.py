from BaseSolver import BaseSolver
from sys import setrecursionlimit as set_stack_limit
import sys
import time

class Bruteforce(BaseSolver):
    def __init__(self, fname):
        super().__init__(fname)
        self.num_bridges, self.cnf = self.hashi.get_CNFs()
        set_stack_limit(200000)

    def solve(self):
        """
        Starts the recursive search from the first bridge variable.
        """
        start_time = time.time()
        solution = self._recursive(1, [])
        end_time = time.time()
        
        if solution:
            self.solution = solution
            print(f"Solution found in {end_time - start_time:.4f} seconds.")
            return True
        return False

    def _recursive(self, var_idx, assign):
        """
        A recursive function that tries True/False for each variable.
        """
        if var_idx > self.num_bridges:
            if self.hashi.is_singly_connected_component(assign):
                return assign
            return None

        if self._is_valid(assign + [var_idx]):
            result = self._recursive(var_idx + 1, assign + [var_idx])
            if result: 
                return result

        if self._is_valid(assign + [-var_idx]):
            result = self._recursive(var_idx + 1, assign + [-var_idx])
            if result: 
                return result
        return None

    def _is_valid(self, current_assign):
        """
        Checks if the current partial assignment violates any CNF clauses.
        """
        assign_set = set(current_assign)
        
        for clause in self.cnf:
            clause_is_dead = True
            
            for literal in clause:
                if literal in assign_set:
                    clause_is_dead = False
                    break
                if -literal not in assign_set:
                    clause_is_dead = False
                    break
            
            if clause_is_dead:
                return False   
        return True
