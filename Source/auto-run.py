import os
algos = ['astar', 'pysat', 'backtracking', 'bruteforce']
for algo in algos:
    for size in [7, 9, 11, 13, 17, 20]:
        for i in range(1, 6):
            if (size > 9):
                print(f"Skipping {algo} for size {size}x{size}")
            res = os.popen(f"python main.py -a {algo} -f Inputs/{size}x{size}/input-0{i}.txt").read()
            print(res)