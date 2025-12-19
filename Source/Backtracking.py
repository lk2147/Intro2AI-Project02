from BaseSolver import BaseSolver
from sys import setrecursionlimit as set_stack_limit
from time import time as set_clock

class Backtracking(BaseSolver):
    def __init__(self, fname, max_iterations = 10):
        super().__init__(fname)
        self.max_iterations = max_iterations
        set_stack_limit(200000)

    def solve(self):
        """
        Use DPLL and unit propagation to solve CNF. Add cut set constraints when failed.
        """
        if self.num_variables == 0:
            print("Empty CNF.")
            return True
        
        start_time = set_clock()
        for _ in range(self.max_iterations):
            self.solution = self._DPLL(self.cnfs.copy(), [])
            if self.solution is None:
                return False
            
            self.solution.sort(key=lambda x: abs(x))
            blocking_clause = self.hashi.get_cut_set(self.solution)
            if blocking_clause is None:
                end_time = set_clock()
                print(f"Solution found in {end_time - start_time:.4f} seconds after {_+1} iterations.")
                return True
            elif blocking_clause:
                self.cnfs.append(blocking_clause)
            else:
                return False
            
    def _DPLL(self, clauses, assignment):
        """
        Fold unit propagation into backtracking via DPLL and parallel pre-processing.
        """
        while clauses:
            unit_literal = 0
            for clause in clauses:
                if len(clause) == 1:
                    unit_literal = clause[0]
                    break
            if unit_literal == 0:
                break
            assignment += [unit_literal]
            new_clauses = []
            for old_clause in clauses:
                if unit_literal in old_clause:
                    continue
                if -unit_literal in old_clause:
                    if len(old_clause) == 1:
                        return None
                    updated_clause = old_clause.copy()
                    updated_clause.remove(-unit_literal)
                    new_clauses.append(updated_clause)
                else:
                    new_clauses.append(old_clause)
            clauses = new_clauses
        if not clauses:
            return assignment

        literal_counts = {}
        minimum_length = (1 << 63)
        for clause in clauses:
            n = len(clause)
            if len(clause) < minimum_length:
                minimum_length = n
        for clause in clauses:
            if len(clause) != minimum_length:
                continue
            for unit_literal in clause:
                literal_counts[unit_literal] = literal_counts.get(unit_literal, 0) + 1
        chosen_literal = max(literal_counts, key=literal_counts.get)
        
        branch_flag = 3
        true_branch = []
        false_branch = []
        for old_clause in clauses:
            if branch_flag == 0:
                return None
            positive = (chosen_literal in old_clause)
            negative = (-chosen_literal in old_clause)
            if not positive and (branch_flag & 1):
                if negative:
                    if len(old_clause) == 1:
                        branch_flag = branch_flag ^ 1
                    else:
                        updated_clause = old_clause.copy()
                        updated_clause.remove(-chosen_literal)
                        true_branch.append(updated_clause)
                else:
                    true_branch.append(old_clause)
            if not negative and (branch_flag & 2):
                if positive:
                    if len(old_clause) == 1:
                        branch_flag = branch_flag ^ 2
                    else:
                        updated_clause = old_clause.copy()
                        updated_clause.remove(chosen_literal)
                        false_branch.append(updated_clause)
                else:
                    false_branch.append(old_clause)
        if (branch_flag & 1):
            ret = self._DPLL(true_branch, assignment + [chosen_literal])
            if ret is not None:
                return ret
        return self._DPLL(false_branch, assignment + [-chosen_literal]) if (branch_flag & 2) else None