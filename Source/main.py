from Backtracking import Backtracking

if __name__ == "__main__":
    solver = Backtracking("D:\\ai\\hashi\\Source\\Inputs\\input-03.txt")
    if solver.solve():
        solver.print_hashi()
    else:
        print("No solution")