from Backtracking import Backtracking
from Bruteforce import Bruteforce
from AStarSolver import AStarSolver

if __name__ == "__main__":
    fname = "Source/Inputs/input-05.txt"
    
    # bf = Bruteforce(fname)
    # if bf.solve():
    #     bf.print_hashi()
    # else:
    #     print("BF NO SOL")
    
    bt = Backtracking(fname)
    if bt.solve():
        bt.print_hashi()
    else:
        print("BT NO SOL")

    astar = AStarSolver(fname)
    if astar.solve():
        astar.print_hashi()
    else:
        print("A* NO SOL")