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
        """
        Solves the Hashi puzzle using DPLL with an iterative check for connectivity.
        1. Solve SAT (CNF).
        2. Check if SAT solution forms a single connected component.
        3. If not, add a blocking clause (negate solution) and repeat.
        """
        start_time = time.time()
        
        # Convert initial CNF to a list of sets for the solver
        # We perform this once, but the list will grow if we find disconnected solutions
        current_clauses = [set(c) for c in self.cnf]
        
        iteration_count = 0

        while True:
            iteration_count += 1
            
            # Run DPLL to find a satisfying assignment for the logic constraints
            # We pass a deep copy or handle the logic such that _dpll doesn't destroy current_clauses 
            # for the next iteration if needed. In this implementation, _dpll creates new lists, 
            # so passing current_clauses is safe.
            raw_assignment = self._dpll(current_clauses, [])

            if raw_assignment is None:
                # If DPLL returns None, the CNF is unsatisfiable (impossible to solve)
                print(f"Unsatisifable after {iteration_count} iterations.")
                return False

            # --- SAT Solution Found, Process it ---
            
            # Map the raw assignment to the format required by Hashi
            # (Positive int for True, Negative int for False)
            assigned_map = {abs(x): x for x in raw_assignment}
            full_model = []
            
            # We only care about the bridge variables (1 to num_bridges) for the Hashi check
            # Auxiliary variables (if any) are handled by the SAT solver but ignored for the graph check
            for i in range(1, self.num_bridges + 1):
                val = assigned_map.get(i, -i) # Default to False if unassigned (though DPLL usually assigns all)
                full_model.append(val)

            # Check the global connectivity constraint
            if self.hashi.is_singly_connected_component(full_model):
                end_time = time.time()
                self.solution = full_model
                print(f"Solution found in {end_time - start_time:.4f} seconds.")
                print(f"Total iterations (Connectivity checks): {iteration_count}")
                return True
            else:
                # --- Valid SAT, but Invalid Graph (Disconnected) ---
                # "Add the negate of the found solution to the CNFs and repeat again"
                
                # Construct Blocking Clause:
                # If model is [A, -B, C], we add clause [-A, B, -C]
                # This ensures we never find this specific disconnected arrangement again.
                blocking_clause = set()
                for lit in raw_assignment:
                    # We optimize by only blocking based on the bridge variables, 
                    # as these define the graph structure.
                    if abs(lit) <= self.num_bridges:
                        blocking_clause.add(-lit)
                
                # Add to the master list of clauses
                current_clauses.append(blocking_clause)
                
                # The loop continues, calling _dpll again with the extra constraint.

    def _dpll(self, clauses, assignment):
        """
        Standard Recursive DPLL with Unit Propagation.
        Does NOT check connectivity; purely solves the SAT boolean math.
        """
        # --- 1. Unit Propagation ---
        while True:
            unit_lit = None
            # Find a unit clause
            for clause in clauses:
                if len(clause) == 1:
                    unit_lit = list(clause)[0]
                    break    

            if unit_lit is None:
                break

            # Add to assignment
            assignment = assignment + [unit_lit]
            
            # Simplify clauses
            new_clauses = []
# A
# A V ... -> True
            for clause in clauses:
                if unit_lit in clause:
                    continue # Clause is true, discard it
                if -unit_lit in clause:
                    # Remove false literal from clause
                    c_copy = clause.copy()
                    c_copy.remove(-unit_lit)
                    if not c_copy:
                        return None # Empty clause = Conflict
                    new_clauses.append(c_copy)
                else:
                    new_clauses.append(clause)
            clauses = new_clauses

        # --- 2. Termination ---
        if not clauses:
            return assignment # All clauses satisfied

        # --- 3. Heuristic / Splitting ---
        # Choose the literal appearing most frequently in the shortest clauses (MOMs-like)
# Maximum Occurences on Minimum sized clauses
        # to satisfy difficult constraints first.
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
            # Fallback if logic above misses edge case
            return assignment
            
        chosen_lit = max(literal_counts, key=literal_counts.get)

        # --- 4. Branching ---
        
        # Branch 1: Try True
        clauses_true = []
        possible_conflict = False
# C
# C V ... -> True
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

        # Branch 2: Try False (i.e., -chosen_lit is True)
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
        
        return None# 