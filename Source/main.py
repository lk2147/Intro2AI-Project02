from Backtracking import Backtracking
from Bruteforce import Bruteforce

if __name__ == "__main__":
    fname = "D:\\ai\\hashi\\Source\\Inputs\\input-02.txt"
    bt = Backtracking(fname)
    # bf = Bruteforce(fname)
    if bt.solve():
        bt.print_hashi()
    else:
        print("BT NO SOL")
    # if bf.solve():
    #     bf.print_hashi()
    # else:
    #     print("BF NO SOL")