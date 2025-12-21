import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
from pathlib import Path

def plot_complexities():
    algo_configs = {
        'PySAT':        {'marker': 'o', 'linestyle': '-',  'color': '#1f77b4', 'label': 'pysat'},
        'AStar':        {'marker': '*', 'linestyle': '--', 'color': '#ff7f0e', 'label': 'astar'},
        'Backtracking': {'marker': 'd', 'linestyle': ':',  'color': '#2ca02c', 'label': 'backtracking'},
        'Bruteforce':   {'marker': 's', 'linestyle': '-.', 'color': '#d62728', 'label': 'bruteforce'}
    }
    metrics = ['Time', 'Memory']
    
    for metric in metrics:
        base_path = Path(f"Outputs/Summary/{metric}")
        if not base_path.exists(): continue

        csv_files = sorted([f for f in os.listdir(base_path) if f.endswith('.csv')], 
                           key=lambda x: int(x.split('x')[0]) if 'x' in x else 0)
        
        if not csv_files: continue

        num_plots = len(csv_files)
        cols = 2
        rows = (num_plots + 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(16, 5 * rows))
        axes = axes.flatten()

        for i, file_name in enumerate(csv_files):
            ax = axes[i]
            df = pd.read_csv(base_path / file_name)
            
            df['input_id'] = df['Input File'].apply(lambda x: str(x).split('-')[-1].split('.')[0])
            
            for algo_key, cfg in algo_configs.items():
                if algo_key in df.columns:
                    y_data = pd.to_numeric(df[algo_key], errors='coerce')
                    
                    if metric == "Time":
                        y_data = y_data * 1000 # convert to milliseconds
                    
                    if not y_data.isna().all():
                        ax.plot(df['input_id'], y_data, 
                                label=cfg['label'], marker=cfg['marker'], 
                                linestyle=cfg['linestyle'], color=cfg['color'], 
                                markersize=8, linewidth=1.5)

            if metric == "Time":
                ax.set_yscale('log')
                ax.set_ylabel("Execution Time (ms) - Log Scale", fontsize=10, fontweight='bold')
                
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
                ax.grid(True, which="both", linestyle='--', alpha=0.4)
            else:
                ax.set_ylabel("Peak Memory (MB)", fontsize=10, fontweight='bold')
                ax.grid(True, linestyle='--', alpha=0.6)

            size_name = file_name.replace('.csv', '')
            ax.set_title(f"Map {size_name} {metric.lower()} comparison", fontsize=13, fontweight='bold', pad=10)
            ax.set_xlabel("Test Case ID", fontsize=9)
            ax.legend(loc='best', fontsize=9, framealpha=0.8)

        for j in range(i + 1, len(axes)): axes[j].axis('off')
        plt.tight_layout()
        
        output_dir = Path("Outputs/Visualization")
        output_dir.mkdir(parents=True, exist_ok=True)
        save_path = output_dir / f"{metric.lower()}_comparison.png"
        plt.savefig(save_path, dpi=200, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
        
    plt.show()

if __name__ == "__main__":
    plot_complexities()