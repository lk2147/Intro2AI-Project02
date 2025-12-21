import heapq
import time
from BaseSolver import BaseSolver
from collections import defaultdict

class CNFState:
    """
    Represents the state of a node in the A* search tree.
    """
    def __init__(self, assignment, unsatisfied_indices, conflict=False):
        # assignment: Dict storing assigned variables {variable: True/False}
        self.assignment = assignment
        
        # unsatisfied_indices: Set containing indices of clauses NOT yet satisfied.
        # Our goal is to make this set empty.
        self.unsatisfied_indices = unsatisfied_indices
        
        # conflict: Flag marking if this state is contradictory (dead end)
        self.conflict = conflict
        
        # h(n): Heuristic - Number of unsatisfied clauses.
        # This is an admissible heuristic because we need at least 1 assignment to resolve 1 clause.
        self.h = len(unsatisfied_indices)
        
        # g(n): Cost - Number of assigned variables.
        self.g = len(assignment)
        self.f = self.g + 5 * self.h  # f(n) = g(n) + h(n)
        
    def __lt__(self, other):
        # Prioritize based on f = g + h
        if self.f != other.f:
            return self.f < other.f
        # Prioritize smallest h (Greedy Best-First Search).
        # In SAT, we care about finding a solution fastest, not necessarily the shortest path,
        # so prioritizing h is more important than g.
        if self.h != other.h:
            return self.h < other.h
        # If h is equal, prioritize states with more assigned variables (go deeper)
        return self.g > other.g

class AStarSolver(BaseSolver):
    def __init__(self, fname):
        super().__init__(fname)
        # 2. Pre-processing - Optimize access speed
        # Map: Variable -> List of indices of clauses containing that variable
        # Example: self.var_to_clauses[1] = [0, 5, 8] (Variable 1 appears in clauses 0, 5, 8)
        self.var_to_clauses = defaultdict(list)
        for idx, clause in enumerate(self.cnfs):
            for lit in clause:
                self.var_to_clauses[abs(lit)].append(idx)

    def solve(self):
        start_time = time.time()
        
        # --- INITIALIZATION ---
        initial_assignment = {}
        # Initially, all clauses are unsatisfied
        all_clause_indices = set(range(len(self.cnfs)))
        # print(all_clause_indices)
        
        # Perform Unit Propagation from the start (handle existing unit clauses)
        initial_assignment, initial_unsatisfied, is_conflict = self._propagate(
            initial_assignment, all_clause_indices
        )
        
        if is_conflict:
            print("CNF Unsatisfiable immediately after initial propagation.")
            return False

        start_node = CNFState(initial_assignment, initial_unsatisfied)
        
        # Priority Queue for A*
        open_set = []
        heapq.heappush(open_set, start_node)
        
        self.nodes_expanded = 0
        
        print("Start searching with A*...")

        # --- MAIN LOOP ---
        while open_set:
            current = heapq.heappop(open_set)
            self.nodes_expanded += 1
            
            # --- 1. GOAL CHECK ---
            if current.h == 0:
                # SAT solution found (logically satisfied)
                # Convert to solution format
                solution_list = self._build_solution_list(current.assignment)
                
                # Check Connectivity (Global Connectivity Constraint)
                # Since CNF only ensures local logic, we need to check if the graph is connected.
                if self.hashi.is_singly_connected_component(solution_list):
                    self.solution = solution_list
                    # print(f"Nodes explored: {nodes_explored}")
                    return True
                else:
                    # If not connected -> This solution is invalid graph-wise -> Skip
                    continue

            # --- 2. VARIABLE SELECTION HEURISTIC ---
            # Select the best variable to branch.
            # We use MOMs strategy: Select the variable appearing most in the shortest clauses.
            var_to_branch = self._select_variable_moms(current)
            
            if var_to_branch is None:
                continue # Deadend

            # --- 3. EXPANSION ---
            # Try assigning True and False to the selected variable
            for value in [True, False]:
                
                # Copy old state to create a new branch
                new_assignment = current.assignment.copy()
                new_assignment[var_to_branch] = value
                
                # Update temporary list of unsatisfied clauses
                # (No need to propagate yet, just update the state of the newly assigned variable)
                temp_unsatisfied, conflict_detected = self._update_clauses_status(
                    current.unsatisfied_indices, var_to_branch, value
                )
                
                if conflict_detected:
                    continue # Prune this branch immediately

                # --- 4. UNIT PROPAGATION ---
                # This is the most important OPTIMIZATION step.
                # From the newly assigned variable, automatically infer other variables that must follow.
                final_assignment, final_unsatisfied, prop_conflict = self._propagate(
                    new_assignment, temp_unsatisfied
                )
                
                if not prop_conflict:
                    # If no conflict, add new node to the queue
                    new_node = CNFState(final_assignment, final_unsatisfied)
                    heapq.heappush(open_set, new_node)

        print(f"No solution found. Nodes explored: {nodes_explored}")
        return False

    def _propagate(self, assignment, unsatisfied_indices):
        """
        Performs Unit Propagation.
        Repeatedly finds clauses with only 1 unassigned variable (Unit Clause)
        and assigns the mandatory value to that variable.
        
        Output: (new assignment, new unsatisfied, is_conflict)
        """
        curr_assignment = assignment
        # print(curr_assignment)
        curr_unsatisfied = unsatisfied_indices
        
        while True:
            unit_vars = {} # Store variables that must be assigned: {var: value}
            
            # Iterate through unsatisfied clauses
            for idx in curr_unsatisfied:
                clause = self.cnfs[idx]
                
                unassigned_lits = []
                is_satisfied = False
                
                for lit in clause:
                    var = abs(lit)
                    if var in curr_assignment:
                        # If variable is assigned and makes the clause True
                        # print(curr_assignment[var])
                        if curr_assignment[var] == (lit > 0):
                            is_satisfied = True
                            break
                    else:
                        unassigned_lits.append(lit)
                
                if is_satisfied:
                    continue
                
                # If clause is unsatisfied and no variables left -> Conflict
                if len(unassigned_lits) == 0:
                    return curr_assignment, curr_unsatisfied, True
                
                # If only exactly 1 variable remains unassigned -> This is a Unit Clause
                if len(unassigned_lits) == 1:
                    lit = unassigned_lits[0]
                    # Mandatory assignment to make clause True
                    val = (lit > 0)
                    var = abs(lit)
                    # print("var:", var, "must be", val)
                    
                    # Check for conflicts with previous inferences in the loop
                    if var in unit_vars and unit_vars[var] != val:
                        return curr_assignment, curr_unsatisfied, True
                    
                    unit_vars[var] = val

            # If no new variables found to infer -> Stop (Fixed point)
            if not unit_vars:
                break
            
            # Apply newly inferred variables to assignment
            for var, val in unit_vars.items():
                curr_assignment[var] = val
                # Update clause list based on newly assigned variable
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
        
        # Only need to check clauses containing var (use index map for speed)
        # But for simplicity and accuracy with the shrinking unsatisfied set, we iterate over unsatisfied.
        # (Can be optimized by intersecting current_unsatisfied and self.var_to_clauses[var])
        
        affected_clauses = current_unsatisfied
        
        for idx in affected_clauses:
            clause = self.cnfs[idx]
            
            # Check clause status
            is_satisfied = False
            has_unassigned = False
            
            for lit in clause:
                l_var = abs(lit)
                
                if l_var == var:
                    # Variable just assigned
                    if (lit > 0) == val:
                        is_satisfied = True
                        break
                # Previously assigned variables don't need assignment dict check 
                # because if it made the clause True, the clause wouldn't be in current_unsatisfied
                # We only care if the clause becomes completely False.
                elif l_var not in self.var_to_clauses: 
                    # Virtual logic: var_to_clauses contains all variables. 
                    # If l_var is unassigned, it remains unassigned.
                    # Correct check: need access to global assignment, but costly.
                    # Since we are in the propagation flow, we know other variables in this clause 
                    # are either assigned False or unassigned.
                    pass
            
            if is_satisfied:
                continue

            # If not satisfied, we must ensure it hasn't Failed
            # (Meaning there's still at least 1 unassigned or True literal)
            # Since we don't pass assignment here for optimization, exact conflict check 
            # is done in _propagate (counting unassigned_lits).
            # In this function, we only filter out clauses that have become True.
            new_unsatisfied.add(idx)
            
        return new_unsatisfied, False

    def _select_variable_moms(self, state):
        """
        MOMs Variable Selection Heuristic (Maximum Occurrences in Minimum length clauses).
        Select the variable appearing most in the shortest clauses (smallest size).
        Goal: Trigger Unit Propagation or Conflict earliest.
        """
        min_len = float('inf')
        counts = defaultdict(int)
        
        # 1. Find the smallest length among unsatisfied clauses
        # Simultaneously count frequency
        candidates = []
        
        for idx in state.unsatisfied_indices:
            clause = self.cnfs[idx]
            
            # Count number of unassigned literals in this clause
            unassigned = [lit for lit in clause if abs(lit) not in state.assignment]
            length = len(unassigned)
            
            if length == 0: continue # Conflict detected (should have been filtered earlier)
            
            if length < min_len:
                min_len = length
                candidates = [] # Reset candidates
                counts.clear() # Reset counts because we only care about min_len
            
            if length == min_len:
                candidates.append(unassigned)
                for lit in unassigned:
                    counts[abs(lit)] += 1
        
        if not counts:
            # Rare case: Clauses remain but no unassigned variables (Conflict)
            return None
            
        # 2. Select variable with highest occurrence count
        return max(counts, key=counts.get)

    def _build_solution_list(self, assignment):
        """Convert dict {1:True, 2:False} to list [1, -2, ...]"""
        sol = []
        for i in range(1, self.num_variables + 1):
            val = assignment.get(i, False) # Default to False if variable is insignificant
            if val:
                sol.append(i)
            else:
                sol.append(-i)
        return sol