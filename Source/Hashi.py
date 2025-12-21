import numpy as np
from pysat import card

class DisjointSet:
    def __init__(self, num_nodes):
        self.par = -np.ones(dtype=int, shape=num_nodes)
        
    def _root(self, v):
        if self.par[v] < 0:
            return v
        self.par[v] = self._root(self.par[v])
        return self.par[v]
    
    def join(self, edge):
        x = self._root(edge[0])
        y = self._root(edge[1])
        if x == y:
            return False
        if self.par[x] > self.par[y]:
            self.par[x], self.par[y] = self.par[y], self.par[x]
        self.par[x] += self.par[y]
        self.par[y] = x
        return True
    
    def is_tree(self):
        return -self.par[self._root(0)] == self.par.shape[0]
    
    def get_root_of_the_largest_componet(self):
        return np.argmin(self.par)
    
    def is_connective_edge(self, root, edge):
        x = self._root(edge[0])
        y = self._root(edge[1])
        return x != y and (x == root or y == root)

class Hashi:
    def __init__(self, fname):
        self.fname = fname
        np.set_printoptions(linewidth=np.inf)
        self.bridge_characters = ['-', '|', '=', '$']
        self._add_CNF_constraints(self._define_logical_variables(fname))
        
    def _define_logical_variables(self, fname):
        """
        Define logical variables and related variable
        - num_island: number of islands
        - islands: tuple of (row, column, value) of the mapped island
        - num_bridges: number of logical variable (bridges)
        - bridges: pair (u, v) of islands' indices
        - edges: vector of indices (plus 1) of bridges from island.
        """
        self.grid = np.loadtxt(fname=fname, dtype=np.uint32)
        horiz_rows, horiz_cols = np.where(self.grid > 0)
        
        self.num_islands = horiz_rows.shape[0]
        island_vals = self.grid[horiz_rows, horiz_cols]
        self.islands = np.column_stack((horiz_rows, horiz_cols, island_vals))
        self.grid += ord('0')
        
        verti_order = np.lexsort((horiz_rows, horiz_cols))
        verti_cols = horiz_cols[verti_order]
        verti_rows = horiz_rows[verti_order]
        
        horiz_indices = np.arange(0, self.num_islands)
        verti_indices = horiz_indices[verti_order]
        
        horiz_mask = (horiz_rows[:-1] == horiz_rows[1:]) & (horiz_cols[:-1] + 1 < horiz_cols[1:])
        verti_mask = (verti_cols[:-1] == verti_cols[1:]) & (verti_rows[:-1] + 1 < verti_rows[1:])
        
        self.num_bridges = (np.sum(horiz_mask) + np.sum(verti_mask)) << 1
        self.bridges = np.empty(dtype=int, shape=(self.num_bridges, 2))
        self.edges = [[] for _ in range(self.num_islands)]
        
        bridge_indices = 0
        for i in np.where(horiz_mask)[0]:
            u, v = horiz_indices[i:i+2]
            for _ in range(2):
                self.bridges[bridge_indices] = (u, v)
                bridge_indices += 1
                self.edges[u].append(bridge_indices)
                self.edges[v].append(bridge_indices)

        split_index = bridge_indices
        for i in np.where(verti_mask)[0]:
            u, v = verti_indices[i:i+2]
            for _ in range(2):
                self.bridges[bridge_indices] = (u, v)
                bridge_indices += 1
                self.edges[u].append(bridge_indices)
                self.edges[v].append(bridge_indices)
        return split_index
    
    def _add_CNF_constraints(self, split_index):
        """
        Generate CNF constraints (exclude the connected component constraint)
        """
        self._add_double_bridges()
        self._add_crossing_bridges(split_index)
        self._add_total_bridges()
        self._add_neighbor_capacity_constraints()
        if self.num_islands > 2:
            self._add_isolation_constraints()
        self._remove_duplicates()
    
    def _add_double_bridges(self):
        self.CNFs = [[i+1, -i-2] for i in range(0, self.num_bridges, 2)]
    
    def _add_crossing_bridges(self, split_index):
        for i in range(0, split_index, 2):
            for j in range(split_index, self.num_bridges, 2):
                if self._is_crossing(self.bridges[i], self.bridges[j]):
                    self.CNFs.append([-i-1, -j-1])
    
    def _is_crossing(self, horiz_bridge, verti_bridge):
        a, b = horiz_bridge
        c, d = verti_bridge
        return  self.islands[c][0] < self.islands[a][0] < self.islands[d][0] and \
                self.islands[a][1] < self.islands[c][1] < self.islands[b][1]
    
    def _add_total_bridges(self):
        top_index = self.num_bridges
        for i in range(self.num_islands):
            deg = self.islands[i][2]
            max_possible = len(self.edges[i])
            if max_possible < deg:
                print(f"Invalid input: island at {self.islands[i][:2]} needs {deg} bridges but can have at most {max_possible}.")
                exit()
            sum_cnfs = card.CardEnc.equals(lits=self.edges[i], bound=deg, top_id=top_index)
            top_index = sum_cnfs.nv
            self.CNFs.extend(sum_cnfs.clauses)
    
    def _add_neighbor_capacity_constraints(self):
        for i in range(self.num_islands):
            val = self.islands[i][2]
            neighbor_vars = self.edges[i]
            num_neighbors = len(neighbor_vars) // 2
            
            if num_neighbors == 0:
                continue

            if val == 2 * num_neighbors:
                for k in range(1, len(neighbor_vars), 2):
                    double_bridge_lit = neighbor_vars[k] 
                    self.CNFs.append([double_bridge_lit])

            elif val == 2 * num_neighbors - 1:
                for k in range(0, len(neighbor_vars), 2):
                    single_bridge_lit = neighbor_vars[k]
                    self.CNFs.append([single_bridge_lit])

    def _add_isolation_constraints(self):
        for i in range(0, self.num_bridges, 2):
            u, v = self.bridges[i]
            val_u = self.islands[u][2]
            val_v = self.islands[v][2]
            if val_u == 1 and val_v == 1:
                self.CNFs.append([-i-1])
            if val_u == 2 and val_v == 2:
                self.CNFs.append([-i-2])

    def _remove_duplicates(self):
        unique_clauses = set()
        for clause in self.CNFs:
            sorted_clause = tuple(sorted(clause))
            unique_clauses.add(sorted_clause)
        self.CNFs = [list(c) for c in unique_clauses]
        print(f"Duplicates removed. Remaining clauses: {len(self.CNFs)}")
    
    def _resolve_bridge(self, r, c, dr, dc, n, bridge_flag):
        rows = r + np.arange(1, n) * dr
        cols = c + np.arange(1, n) * dc
        self.grid[rows, cols] = ord(self.bridge_characters[bridge_flag])
    
    def get_number_of_variables(self):
        return self.num_bridges
    
    def get_CNFs(self):
        return self.CNFs.copy()
    
    def is_singly_connected_component(self, result):
        dsu = DisjointSet(self.num_islands)
        for i in range(0, self.num_bridges, 2):
            if result[i] > 0:
                dsu.join(self.bridges[i])
        return dsu.is_tree()

    def get_cut_set(self, result):
        """
        Check if the solution form one connected component.\
        Return a cut set for the larget component if it is not.
        """
        dsu = DisjointSet(self.num_islands)
        for i in range(0, self.num_bridges, 2):
            if result[i] > 0:
                dsu.join(self.bridges[i])
        if dsu.is_tree():
            return None
        
        cut_set = []
        root = dsu.get_root_of_the_largest_componet()
        for i in range(0, self.num_bridges, 2):
            if result[i] < 0 and dsu.is_connective_edge(root, self.bridges[i]):
                cut_set.append(i + 1)
        return cut_set

    def print_solution(self, result):
        # output_file = self.fname.replace("Inputs", "Outputs").replace("input", "output")
        self.export_cnf("Outputs/constraints.cnf")
        output_file = "Outputs/solution.txt"
        if len(result) < self.num_bridges:
            return

        for i in range(0, self.num_bridges, 2):
            if result[i] < 0:
                continue
            u, v = self.bridges[i]
            r = self.islands[u][0]
            c = self.islands[u][1]
            dr = self.islands[v][0] - r
            dc = self.islands[v][1] - c
            n = dr + dc
            if dr > 0:
                dr = 1
            else:
                dc = 1
            bridge_flag = 1 if dr > 0 else 0
            if result[i+1] > 0:
                bridge_flag |= 2
            self._resolve_bridge(r, c, dr, dc, n, bridge_flag)
        
        print(self.grid.view('U1'))

        if output_file:
            try:
                import os
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                with open(output_file, 'w', encoding='utf-8') as f:
                    rows, cols = self.grid.shape
                    for r in range(rows):
                        row_chars = []
                        for c in range(cols):
                            char_val = chr(int(self.grid[r, c]))
                            row_chars.append(char_val)
                        
                        f.write(" ".join(row_chars) + "\n")
                
                print(f"Solution saved to: {output_file}")
            except IOError as e:
                print(f"Error writing to file {output_file}: {e}")
    
    def export_cnf(self, output_filename):
        """
        Export the CNF clauses to a DIMACS format file.
        """
        max_var = 0
        for clause in self.CNFs:
            for literal in clause:
                if abs(literal) > max_var:
                    max_var = abs(literal)
        
        num_clauses = len(self.CNFs)

        try:
            with open(output_filename, 'w') as f:
                f.write(f"p cnf {max_var} {num_clauses}\n")
                
                for clause in self.CNFs:
                    line = " ".join(map(str, clause))
                    f.write(f"{line} 0\n")
            
            print(f"Wrote CNF to {output_filename} successfully.")
            
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")
            