from Backtracking import Backtracking

if __name__ == "__main__":
    solver = Backtracking("Inputs/input-01.txt")
    if solver.solve():
        solver.print_hashi()
    else:
        print("No solution")