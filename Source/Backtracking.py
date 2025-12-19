from BaseSolver import BaseSolver
import sys
import time

class Backtracking(BaseSolver):
    def __init__(self, fname):
        super().__init__(fname)
        self.num_bridges, self.cnf = self.hashi.get_CNFs()
        # Increase recursion limit for deep search trees in difficult puzzles
        sys.setrecursionlimit(20000)

    def solve(self):
        start_time = time.time()
        current_clauses = [set(c) for c in self.cnf]
        iteration_count = 0

        while True:
            iteration_count += 1
            raw_assignment = self._dpll(current_clauses, [])

            if raw_assignment is None:
                return False

            assigned_map = {abs(x): x for x in raw_assignment}
            full_model = []
            for i in range(1, self.num_bridges + 1):
                val = assigned_map.get(i, -i)
                full_model.append(val)

            components = self.hashi.get_components(full_model)

            if len(components) == 1:
                end_time = time.time()
                self.solution = full_model
                print(f"Solution found in {end_time - start_time:.4f} seconds.")
                return True
            else:
                S = components[0]
                
                # Tìm tập cắt: Những cạnh có thể giúp S thoát khỏi cô lập
                cut_vars = self.hashi.get_cut_set_vars(S)
                
                # blocking_clause = (x1 v x2 v ... v xn)
                if cut_vars:
                    blocking_clause = set(cut_vars)
                    current_clauses.append(blocking_clause)
                else:
                    return False

    def _dpll(self, clauses, assignment):
        """
        Recursive DPLL with Unit Propagation.
        Does NOT check connectivity; purely solves the SAT boolean math.
        """
        # Unit Propagation 
        while True:
            unit_lit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit_lit = list(clause)[0]
                    break    

            if unit_lit is None:
                break

            assignment = assignment + [unit_lit]

            new_clauses = []

            for clause in clauses:
                if unit_lit in clause:
                    continue 
                if -unit_lit in clause:
                    c_copy = clause.copy()
                    c_copy.remove(-unit_lit)
                    if not c_copy:
                        return None
                    new_clauses.append(c_copy)
                else:
                    new_clauses.append(clause)
            clauses = new_clauses

        if not clauses:
            return assignment 

        literal_counts = {}
        min_len = (1 << 63)
        for c in clauses:
            if len(c) < min_len:
                min_len = len(c)
        
        for c in clauses:
            if len(c) == min_len:
                for lit in c:
                    literal_counts[lit] = literal_counts.get(lit, 0) + 1
        
        if not literal_counts:
            return assignment
            
        chosen_lit = max(literal_counts, key=literal_counts.get)
        
        # Branch 1: Try True
        clauses_true = []
        possible_conflict = False

        for clause in clauses:
            if chosen_lit in clause:
                continue
            if -chosen_lit in clause:
                c_copy = clause.copy()
                c_copy.remove(-chosen_lit)
                if not c_copy:
                    possible_conflict = True
                    break
                clauses_true.append(c_copy)
            else:
                clauses_true.append(clause)
        
        if not possible_conflict:
            res = self._dpll(clauses_true, assignment + [chosen_lit])
            if res is not None:
                return res

        # Branch 2: Try False
        neg_lit = -chosen_lit
        clauses_false = []
        possible_conflict = False
        for clause in clauses:
            if neg_lit in clause: continue
            if -neg_lit in clause:
                c_copy = clause.copy()
                c_copy.remove(-neg_lit)
                if not c_copy:
                    possible_conflict = True
                    break
                clauses_false.append(c_copy)
            else:
                clauses_false.append(clause)

        if not possible_conflict:
            res = self._dpll(clauses_false, assignment + [neg_lit])
            if res is not None:
                return res
        
        return None