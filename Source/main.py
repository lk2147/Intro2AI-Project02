from Backtracking import Backtracking
from Bruteforce import Bruteforce
from AStarSolver import AStarSolver

if __name__ == "__main__":
    fname = "./Inputs/input-06.txt"
    bt = Backtracking(fname)
    bf = Bruteforce(fname)
    # if bt.solve():
    #     bt.print_hashi()
    # else:
    #     print("BT NO SOL")

    # if bf.solve():
    #     bf.print_hashi()
    # else:
    #     print("BF NO SOL")

    astar = AStarSolver(fname)
    if astar.solve():
        astar.print_hashi()
    else:
        print("A* NO SOL")