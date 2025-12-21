import heapq
from BaseSolver import BaseSolver
from collections import defaultdict

class CNFState:
    """
    Represents the state of a node in the A* search tree.
    """
    def __init__(self, assignment, unsatisfied_indices, conflict=False):
        self.assignment = assignment
        self.unsatisfied_indices = unsatisfied_indices
        self.conflict = conflict
        self.h = len(unsatisfied_indices)
        self.g = len(assignment)
        self.f = self.g + self.h
        
    def __lt__(self, other):
        """
        Compare function, return true if the smaller f = g + h is prioritized.
        If f is equal, prioritize the one with smaller h because solving SAT mean finding the fastest way to get to the solution.
        If h is equal, prioritize the one with greater g because resolving more variables mean closer to either the solution or dead end.
        """
        if self.f != other.f:
            return self.f < other.f
        if self.h != other.h:
            return self.h < other.h
        return self.g > other.g

class AStarSolver(BaseSolver):
    def __init__(self, fname):
        super().__init__(fname)
        self.var_to_clauses = defaultdict(list)
        for idx, clause in enumerate(self.cnfs):
            for lit in clause:
                self.var_to_clauses[abs(lit)].append(idx)

    def solve(self):
        initial_assignment = {}
        all_clause_indices = set(range(len(self.cnfs)))        
        initial_assignment, initial_unsatisfied, is_conflict = self._propagate(
            initial_assignment, all_clause_indices
        )
        if is_conflict:
            print("CNF Unsatisfiable immediately after initial propagation.")
            return False

        start_node = CNFState(initial_assignment, initial_unsatisfied)
        open_set = []
        heapq.heappush(open_set, start_node)
        
        while open_set:
            current = heapq.heappop(open_set)
            self.nodes_expanded += 1
            
            if current.h == 0:
                solution_list = self._build_solution_list(current.assignment)
                if self.hashi.is_singly_connected_component(solution_list):
                    self.solution = solution_list
                    return True
                else:
                    continue

            var_to_branch = self._select_variable_moms(current)            
            if var_to_branch is None:
                continue

            for value in [True, False]:
                new_assignment = current.assignment.copy()
                new_assignment[var_to_branch] = value
                temp_unsatisfied, conflict_detected = self._update_clauses_status(
                    current.unsatisfied_indices, var_to_branch, value
                )
                if conflict_detected:
                    continue

                final_assignment, final_unsatisfied, prop_conflict = self._propagate(
                    new_assignment, temp_unsatisfied
                )                
                if not prop_conflict:
                    new_node = CNFState(final_assignment, final_unsatisfied)
                    heapq.heappush(open_set, new_node)
                    
        print(f"No solution found. Nodes explored: {self.nodes_expanded}")
        return False

    def _propagate(self, assignment, unsatisfied_indices):
        """
        Performs Unit Propagation.
        Repeatedly finds clauses with only 1 unassigned variable (Unit Clause)
        and assigns the mandatory value to that variable.
        
        Output: (new assignment, new unsatisfied, is_conflict)
        """
        curr_assignment = assignment
        curr_unsatisfied = unsatisfied_indices
        
        while True:
            unit_vars = {}
            
            for idx in curr_unsatisfied:
                clause = self.cnfs[idx]
                
                unassigned_lits = []
                is_satisfied = False
                
                for lit in clause:
                    var = abs(lit)
                    if var in curr_assignment:
                        if curr_assignment[var] == (lit > 0):
                            is_satisfied = True
                            break
                    else:
                        unassigned_lits.append(lit)
                
                if is_satisfied:
                    continue
                
                if len(unassigned_lits) == 0:
                    return curr_assignment, curr_unsatisfied, True
                
                if len(unassigned_lits) == 1:
                    lit = unassigned_lits[0]
                    val = (lit > 0)
                    var = abs(lit)
                    
                    if var in unit_vars and unit_vars[var] != val:
                        return curr_assignment, curr_unsatisfied, True
                    
                    unit_vars[var] = val

            if not unit_vars:
                break
            
            for var, val in unit_vars.items():
                curr_assignment[var] = val
                curr_unsatisfied, conflict = self._update_clauses_status(
                    curr_unsatisfied, var, val
                )
                if conflict:
                    return curr_assignment, curr_unsatisfied, True
                    
        return curr_assignment, curr_unsatisfied, False

    def _update_clauses_status(self, current_unsatisfied, var, val):
        """
        Updates the set of unsatisfied clauses after assigning var = val.
        Returns: (new set, boolean is_conflict)
        """
        new_unsatisfied = set()
        affected_clauses = current_unsatisfied        
        for idx in affected_clauses:
            clause = self.cnfs[idx]
            
            is_satisfied = False            
            for lit in clause:
                l_var = abs(lit)
                
                if l_var == var:
                    if (lit > 0) == val:
                        is_satisfied = True
                        break
                elif l_var not in self.var_to_clauses: 
                    pass
            
            if is_satisfied:
                continue
            new_unsatisfied.add(idx)
        return new_unsatisfied, False

    def _select_variable_moms(self, state):
        """
        Apply MOMs Variable Selection Heuristic (Maximum Occurrences in Minimum length clauses).
        """
        min_len = float('inf')
        counts = defaultdict(int)
        
        for idx in state.unsatisfied_indices:
            clause = self.cnfs[idx]
            
            unassigned = [lit for lit in clause if abs(lit) not in state.assignment]
            length = len(unassigned)
            if length == 0: continue
            
            if length < min_len:
                min_len = length
                candidates = []
                counts.clear()
            
            if length == min_len:
                candidates.append(unassigned)
                for lit in unassigned:
                    counts[abs(lit)] += 1
        
        if not counts:
            return None            
        return max(counts, key=counts.get)

    def _build_solution_list(self, assignment):
        sol = []
        for i in range(1, self.num_variables + 1):
            val = assignment.get(i, False)
            if val:
                sol.append(i)
            else:
                sol.append(-i)
        return sol