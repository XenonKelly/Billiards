import numpy as np
import matplotlib.pyplot as plt

def plot_collision_distribution(arr, color='#ff7f0e', show_values=True, grid=True):
    indices = np.arange(len(arr))  
    values = np.array(arr)         
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(indices, values, color=color, alpha=0.7, edgecolor='black')
    
    plt.xlabel('Сколько шариков, летящих к стене, столкнулись хотя бы с одним шариком', fontsize=12)
    plt.ylabel('Сколько моментов dt такая картина повторялась', fontsize=12)
    plt.title('Распределение вероятности столкновений в системе', fontsize=14, pad=20)
    plt.xticks(indices)  
    
    if grid:
        plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    if show_values:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height}',
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()