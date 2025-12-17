from BaseSolver import BaseSolver
import sys
import time

class Bruteforce(BaseSolver):
    def __init__(self, fname):
        super().__init__(fname)
        self.num_bridges, self.cnf = self.hashi.get_CNFs()
        # Essential for deep search trees
        sys.setrecursionlimit(20000)

    def solve(self):
        """
        Starts the recursive search from the first bridge variable.
        """
        # We start with variable index 1 and an empty assignment list
        start_time = time.time()
        solution = self._recursive_solve(1, [])
        end_time = time.time()
        
        if solution:
            self.solution = solution
            print(f"Solution found in {end_time - start_time:.4f} seconds.")
            return True
        return False

    def _recursive_solve(self, var_idx, assignment):
        """
        A simple recursive function that tries True/False for each variable.
        """
        
        # --- Base Case: All variables assigned ---
        if var_idx > self.num_bridges:
            # If we reached here, the SAT logic is valid (passed all pruning checks).
            # Now perform the final expensive check: Graph Connectivity.
            if self.hashi.is_singly_connected_component(assignment):
                return assignment
            return None

        # --- Recursive Step ---
        
        # Branch 1: Try setting current bridge to TRUE
        # We assume True (var_idx) and check if it breaks anything immediately.
        if self._is_valid_so_far(assignment + [var_idx]):
            result = self._recursive_solve(var_idx + 1, assignment + [var_idx])
            if result: return result

        # Branch 2: Try setting current bridge to FALSE
        # We assume False (-var_idx) and check if it breaks anything immediately.
        if self._is_valid_so_far(assignment + [-var_idx]):
            result = self._recursive_solve(var_idx + 1, assignment + [-var_idx])
            if result: return result

        # If both True and False fail, this path is dead. Backtrack.
        return None

    def _is_valid_so_far(self, current_assignment):
        """
        Checks if the current partial assignment violates any CNF clauses.
        This is the 'Pruning' step that makes the bruteforce effective.
        """
        # Convert list to set for O(1) lookup speed
        assign_set = set(current_assignment)
        
        for clause in self.cnf:
            # Logic: A clause is valid if at least one literal is True.
            # A clause is BROKEN only if ALL its literals are False.
            
            clause_is_dead = True
            
            for lit in clause:
                if lit in assign_set:
                    # Clause is satisfied (True). We can stop checking this clause.
                    clause_is_dead = False
                    break
                
                # Check if the literal is unassigned.
                # If 'lit' is not in set, AND '-lit' is not in set, it's unassigned.
                if -lit not in assign_set:
                    # Clause is not dead yet, because this unassigned variable 
                    # might become True later.
                    clause_is_dead = False
                    break
            
            # If we iterated through a clause and found NO True literals 
            # and NO unassigned literals (meaning all were False), 
            # then we have broken the puzzle rules.
            if clause_is_dead:
                return False
                
        return True