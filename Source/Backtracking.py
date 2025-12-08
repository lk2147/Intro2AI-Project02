from BaseSolver import BaseSolver
from collections import defaultdict, deque

class Clause:
    def __init__(self, lits):
        self.lits = lits
        if len(lits) >= 2:
            self.watch = [0, 1]
        else:
            self.watch = [0, 0]

class Backtracking(BaseSolver):
    def __init__(self, fname, num_iterations=10):
        super().__init__(fname)
        self.num_variables, self.CNFs = self.hashi.get_CNFs()
        self.clauses = [Clause(c) for c in self.CNFs]
        self.num_iterations = num_iterations

        # compute maximum variable index present in CNF (to include auxiliaries)
        self.max_var = 0
        for c in self.CNFs:
            for lit in c:
                self.max_var = max(self.max_var, abs(lit))

        # assignment array indexed by variable id: None / True / False
        self.assign = [None] * (self.max_var + 1)

        # watched literal -> list[Clause]
        self.watch_list = defaultdict(list)

        # propagation queue (literals)
        self.queue = deque()

        # initialize watches and push initial unit assignments
        self.unsat = False
        for clause in self.clauses:
            if len(clause.lits) == 0:
                self.unsat = True
                return

            if len(clause.lits) == 1:
                if not self._assign_literal(clause.lits[0]):
                    self.unsat = True
                    return
            else:
                L1 = clause.lits[clause.watch[0]]
                L2 = clause.lits[clause.watch[1]]
                self.watch_list[L1].append(clause)
                self.watch_list[L2].append(clause)

        # initial propagation
        if not self._unit_propagate():
            self.unsat = True

    # ---------------- utilities ----------------
    def _is_true(self, lit):
        v = abs(lit)
        if v >= len(self.assign):
            return None
        a = self.assign[v]
        if a is None:
            return None
        return a == (lit > 0)

    def _is_false(self, lit):
        res = self._is_true(lit)
        return res is False

    def _assign_literal(self, lit):
        """Assign literal; return False if contradiction."""
        v = abs(lit)
        val = lit > 0

        # expand assign array if needed (shouldn't be needed because we precomputed max_var,
        # but keep safe)
        if v >= len(self.assign):
            extend_by = v - (len(self.assign) - 1)
            self.assign.extend([None] * extend_by)

        if self.assign[v] is not None:
            return self.assign[v] == val
        self.assign[v] = val
        self.queue.append(lit)
        return True

    # ---------------- watched-literal propagation ----------------
    def _unit_propagate(self):
        while self.queue:
            lit = self.queue.popleft()
            neg = -lit

            # snapshot of affected clauses (we may mutate watch_list)
            affected = list(self.watch_list.get(neg, []))

            for clause in affected:
                # find which watched position corresponds to 'neg'
                if clause.lits[clause.watch[0]] == neg:
                    i = 0
                    j = 1
                else:
                    i = 1
                    j = 0

                # try to find replacement literal for watch[i]
                found_new_watch = False
                for k, L in enumerate(clause.lits):
                    if k == clause.watch[j]:
                        continue
                    if not self._is_false(L):
                        # move watch from neg -> L
                        # remove clause from watch_list[neg] and add to watch_list[L]
                        # safe because we used a snapshot 'affected' to iterate
                        try:
                            self.watch_list[neg].remove(clause)
                        except ValueError:
                            # it's possible it was already removed elsewhere; ignore
                            pass
                        clause.watch[i] = k
                        self.watch_list[L].append(clause)
                        found_new_watch = True
                        break

                if found_new_watch:
                    continue

                # no replacement found, check the other watched literal
                other_lit = clause.lits[clause.watch[j]]

                if self._is_false(other_lit):
                    # clause cannot be satisfied
                    return False

                if self._is_true(other_lit):
                    # clause already satisfied
                    continue

                # unit clause -> force other_lit
                if not self._assign_literal(other_lit):
                    return False

        return True

    # ---------------- backtracking search ----------------
    def _go(self, v):
        """DPLL search targeting real variables 1..num_variables."""
        # finished all real variables
        if v > self.num_variables:
            return True

        # if variable already assigned (maybe forced by propagation), skip
        if self.assign[v] is not None:
            return self._go(v + 1)

        # try True
        saved = self._save_state()
        if self._assign_literal(v):
            if self._unit_propagate():
                if self._go(v + 1):
                    return True
        self._restore_state(saved)

        # try False
        saved = self._save_state()
        if self._assign_literal(-v):
            if self._unit_propagate():
                if self._go(v + 1):
                    return True
        self._restore_state(saved)

        return False

    # ---------------- state save / restore ----------------
    def _save_state(self):
        # copy assign list, shallow-copy clauses' watch indices, copy watch_list lists, queue
        assign_copy = self.assign[:]  # primitives (None/Bool)
        # make a shallow map of watch_list where each list is copied
        watch_copy = {k: v[:] for k, v in self.watch_list.items()}
        # copy watches inside clauses (they are small two-int lists)
        clause_watches = [clause.watch[:] for clause in self.clauses]
        queue_copy = deque(self.queue)
        return (assign_copy, watch_copy, clause_watches, queue_copy)

    def _restore_state(self, state):
        assign_copy, watch_copy, clause_watches, queue_copy = state
        self.assign = assign_copy
        # rebuild watch_list from watch_copy
        self.watch_list = defaultdict(list, {k: v[:] for k, v in watch_copy.items()})
        # restore clause watch indices
        for clause, w in zip(self.clauses, clause_watches):
            clause.watch = w[:]
        self.queue = deque(queue_copy)

    # ---------------- solve ----------------
    def solve(self):
        if self.unsat:
            return False
        for _ in range(self.num_iterations):
            if not self._go(1):
                return False
            self.solution = [i if self.assign[i] else -i for i in range(1, self.num_variables + 1)]
            if self.hashi.is_singly_connected_component(self.solution):
                return True
        return False