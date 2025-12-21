from sys import setrecursionlimit as set_stack_limit
from BaseSolver import BaseSolver

class Bruteforce(BaseSolver):
    def __init__(self, fname):
        super().__init__(fname)
        set_stack_limit(200000)

    def solve(self):
        """
        Starts the recursive search from the first bridge variable.
        """
        self.solution = self._recursive(1, [])        
        if self.solution:
            return True
        return False

    def _recursive(self, var_idx, assign):
        """
        A recursive function that tries True/False for each variable.
        """
        self.nodes_expanded += 1
        if var_idx > self.num_variables:
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
        Checks if the current partial assignment violates any cnfs clauses.
        """
        assign_set = set(current_assign)
        
        for clause in self.cnfs:
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