import argparse
import time
import tracemalloc
import os
import csv
import re
from pathlib import Path
import shutil

from Bruteforce import Bruteforce
from Backtracking import Backtracking
from AStarSolver import AStarSolver
from PySATSolver import PySATSolver

def get_solver(algorithm, fname):
    if algorithm == 'bruteforce':
        return Bruteforce(fname)
    elif algorithm == 'backtracking':
        return Backtracking(fname)
    elif algorithm == 'astar':
        return AStarSolver(fname)
    elif algorithm == 'pysat':
        return PySATSolver(fname)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

def _ensure_dir(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def _read_csv(file_path):
    rows = []
    if os.path.isfile(file_path):
        with open(file_path, mode='r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    return rows

def _write_csv_data(file_path, fieldnames, rows):
    def sort_key(r):
        match = re.search(r'input-(\d+)', r['Input File'])
        return int(match.group(1)) if match else 0
    
    rows.sort(key=sort_key)
    
    with open(file_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def _update_simple_csv(file_path, input_filename, algo_col, value):
    """Dùng cho Time và Memory (chỉ có cột tên thuật toán)"""
    fieldnames = ['Input File', 'Bruteforce', 'Backtracking', 'AStar', 'PySAT']
    _ensure_dir(file_path)
    rows = _read_csv(file_path)
    
    row_updated = False
    for row in rows:
        if row['Input File'] == input_filename:
            row[algo_col] = value
            row_updated = True
            break
    
    if not row_updated:
        new_row = {field: '' for field in fieldnames}
        new_row['Input File'] = input_filename
        new_row[algo_col] = value
        rows.append(new_row)
        
    _write_csv_data(file_path, fieldnames, rows)

def _update_stats_csv(file_path, input_filename, algo_name, node_val, puzzle_info):
    fieldnames = [
        'Input File', 
        'Islands', 'Variables', 'Clauses',
        'Bruteforce Nodes', 'Backtracking Iterations', 'AStar Nodes', 'PySAT Iterations'
    ]
    
    col_map = {
        'Bruteforce': 'Bruteforce Nodes',
        'Backtracking': 'Backtracking Iterations',
        'AStar': 'AStar Nodes',
        'PySAT': 'PySAT Iterations'
    }
    target_col = col_map.get(algo_name)
    
    _ensure_dir(file_path)
    rows = _read_csv(file_path)
    
    row_updated = False
    for row in rows:
        if row['Input File'] == input_filename:
            row['Islands'] = puzzle_info['islands']
            row['Variables'] = puzzle_info['variables']
            row['Clauses'] = puzzle_info['clauses']
            
            if target_col:
                row[target_col] = str(node_val)
            
            row_updated = True
            break
    
    if not row_updated:
        new_row = {field: '' for field in fieldnames}
        new_row['Input File'] = input_filename
        new_row['Islands'] = puzzle_info['islands']
        new_row['Variables'] = puzzle_info['variables']
        new_row['Clauses'] = puzzle_info['clauses']
        if target_col:
            new_row[target_col] = str(node_val)
        rows.append(new_row)
        
    _write_csv_data(file_path, fieldnames, rows)

def update_summary(input_path, algorithm_name, time_val, mem_val, node_val, puzzle_info):
    path_obj = Path(input_path)
    filename = path_obj.name
    
    parent_dir = path_obj.parent.name 
    if "x" not in parent_dir:
        parent_dir = "General"
    
    csv_name = f"{parent_dir}.csv"
    
    time_csv = os.path.join("Outputs", "Summary", "Time", csv_name)
    _update_simple_csv(time_csv, filename, algorithm_name, f"{time_val:.4f}")
    
    mem_csv = os.path.join("Outputs", "Summary", "Memory", csv_name)
    _update_simple_csv(mem_csv, filename, algorithm_name, f"{mem_val:.4f}")
    
    stats_csv = os.path.join("Outputs", "Summary", "Stats", csv_name)
    _update_stats_csv(stats_csv, filename, algorithm_name, node_val if node_val is not None else "", puzzle_info)
    
    print(f"Summary updated: {parent_dir}")

def main():
    parser = argparse.ArgumentParser(description="Hashiwokakero Solver")
    parser.add_argument('-a', '--algorithm', type=str, required=True, 
                        choices=['bruteforce', 'backtracking', 'astar', 'pysat'],
                        help="Algorithm to use")
    parser.add_argument('-f', '--file', type=str, required=True, 
                        help="Path to the input file")
    
    args = parser.parse_args()
    
    algo_map = {
        'bruteforce': 'Bruteforce',
        'backtracking': 'Backtracking',
        'astar': 'AStar',
        'pysat': 'PySAT'
    }
    algo_display = algo_map.get(args.algorithm, 'Unknown')

    print(f"Running {algo_display} on {args.file}...")

    try:
        solver = get_solver(args.algorithm, args.file)
    except Exception as e:
        print(f"Error initializing solver: {e}")
        return

    puzzle_info = {
        'islands': solver.hashi.num_islands,
        'variables': solver.hashi.get_number_of_variables(),
        'clauses': len(solver.hashi.CNFs)
    }

    tracemalloc.start()
    start_time = time.time()
    
    try:
        result = solver.solve()
    except Exception as e:
        print(f"Runtime Error: {e}")
        result = False

    end_time = time.time()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    time_elapsed = end_time - start_time
    memory_peak_mb = peak_mem / (1024 * 1024)
    
    metric_val = solver.nodes_expanded

    if result:
        print(f"SOLVED! Time: {time_elapsed:.4f}s | Memory: {memory_peak_mb:.4f}MB")
        solver.print_hashi() 

        output_path = Path(args.file.replace("Inputs", f"Outputs/{args.algorithm}").replace("input", "output"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move("Outputs/solution.txt", output_path)

        cnf_path = Path(args.file.replace("Inputs", f"Outputs/cnf").replace("input", "constraints").replace(".txt", ".cnf"))
        cnf_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move("Outputs/constraints.cnf", cnf_path)

    else:
        print("NO SOLUTION FOUND.")

    update_summary(args.file, algo_display, time_elapsed, memory_peak_mb, metric_val, puzzle_info)

if __name__ == "__main__":
    main()
