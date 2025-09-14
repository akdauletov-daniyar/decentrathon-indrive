#!/usr/bin/env python3
"""
Create visualizations for STGCN training results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def create_training_plots():
    """Create training progress visualizations"""
    print("Creating training visualizations...")
    
    # Simulate training data based on our results
    epochs = np.arange(1, 11)
    
    # Astana dataset training progress
    astana_train_loss = [1.016797, 1.001952, 1.001545, 1.001265, 1.001576, 
                        1.001179, 1.001353, 1.001238, 1.001158, 1.001268]
    astana_val_loss = [1.009322, 1.008371, 1.008429, 1.008155, 1.007967,
                      1.007946, 1.008006, 1.007905, 1.008085, 1.007865]
    
    # METR-LA dataset training progress
    metr_epochs = np.arange(1, 6)
    metr_train_loss = [0.320536, 0.291240, 0.266591, 0.262864, 0.257877]
    metr_val_loss = [0.377475, 0.313018, 0.312852, 0.310627, 0.311809]
    
    # Create plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Astana training loss
    ax1.plot(epochs, astana_train_loss, 'b-', label='Training Loss', linewidth=2)
    ax1.plot(epochs, astana_val_loss, 'r-', label='Validation Loss', linewidth=2)
    ax1.set_title('Astana Dataset - Training Progress', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss (MSE)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # METR-LA training loss
    ax2.plot(metr_epochs, metr_train_loss, 'b-', label='Training Loss', linewidth=2)
    ax2.plot(metr_epochs, metr_val_loss, 'r-', label='Validation Loss', linewidth=2)
    ax2.set_title('METR-LA Dataset - Training Progress', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss (MSE)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Performance comparison
    datasets = ['Astana', 'METR-LA']
    mae_values = [1.619081, 6.043305]
    rmse_values = [2.017868, 10.503453]
    wmape_values = [5.51, 11.90]
    
    x = np.arange(len(datasets))
    width = 0.25
    
    ax3.bar(x - width, mae_values, width, label='MAE', alpha=0.8)
    ax3.bar(x, rmse_values, width, label='RMSE', alpha=0.8)
    ax3.bar(x + width, wmape_values, width, label='WMAPE (%)', alpha=0.8)
    ax3.set_title('Performance Metrics Comparison', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Dataset')
    ax3.set_ylabel('Error Value')
    ax3.set_xticks(x)
    ax3.set_xticklabels(datasets)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Dataset characteristics
    sensors = [100, 207]
    timesteps = [1000, 34272]
    
    ax4.bar(x - width/2, sensors, width, label='Sensors', alpha=0.8, color='skyblue')
    ax4_twin = ax4.twinx()
    ax4_twin.bar(x + width/2, timesteps, width, label='Timesteps', alpha=0.8, color='lightcoral')
    ax4.set_title('Dataset Characteristics', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Dataset')
    ax4.set_ylabel('Number of Sensors', color='blue')
    ax4_twin.set_ylabel('Number of Timesteps', color='red')
    ax4.set_xticks(x)
    ax4.set_xticklabels(datasets)
    ax4.legend(loc='upper left')
    ax4_twin.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('training_results.png', dpi=300, bbox_inches='tight')
    print("✅ Training plots saved as 'training_results.png'")
    
    return fig

def create_traffic_pattern_visualization():
    """Create traffic pattern visualization"""
    print("Creating traffic pattern visualization...")
    
    # Load Astana data
    if os.path.exists('data/astana/vel.csv'):
        data = pd.read_csv('data/astana/vel.csv', header=None)
        
        # Create heatmap of traffic patterns
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Traffic heatmap (first 100 timesteps, all sensors)
        im1 = ax1.imshow(data.iloc[:100, :].T, cmap='YlOrRd', aspect='auto')
        ax1.set_title('Astana Traffic Patterns (First 100 Timesteps)', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Time Steps')
        ax1.set_ylabel('Sensors (Grid Position)')
        plt.colorbar(im1, ax=ax1, label='Speed (km/h)')
        
        # Average speed over time
        avg_speed = data.mean(axis=1)
        ax2.plot(avg_speed[:200], 'b-', linewidth=2)
        ax2.set_title('Average Traffic Speed Over Time', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Time Steps')
        ax2.set_ylabel('Average Speed (km/h)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('traffic_patterns.png', dpi=300, bbox_inches='tight')
        print("✅ Traffic patterns saved as 'traffic_patterns.png'")
        
        return fig

def create_model_architecture_diagram():
    """Create STGCN architecture diagram"""
    print("Creating model architecture diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # STGCN Architecture
    components = [
        "Input\n(12 timesteps × 100 sensors)",
        "Temporal Conv\n(GLU Activation)",
        "Graph Conv\n(Chebyshev)",
        "Temporal Conv\n(GLU Activation)",
        "Layer Norm\n+ Dropout",
        "Temporal Conv\n(GLU Activation)",
        "Graph Conv\n(Chebyshev)",
        "Temporal Conv\n(GLU Activation)",
        "Layer Norm\n+ Dropout",
        "Output\n(3 timesteps × 100 sensors)"
    ]
    
    # Create flow diagram
    y_positions = np.linspace(0.9, 0.1, len(components))
    
    for i, (comp, y) in enumerate(zip(components, y_positions)):
        # Draw component box
        if i == 0 or i == len(components) - 1:
            color = 'lightblue'
        elif 'Temporal' in comp:
            color = 'lightgreen'
        elif 'Graph' in comp:
            color = 'lightcoral'
        else:
            color = 'lightyellow'
            
        rect = plt.Rectangle((0.1, y-0.03), 0.8, 0.06, 
                           facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        
        # Add text
        ax.text(0.5, y, comp, ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Draw arrow
        if i < len(components) - 1:
            ax.arrow(0.5, y-0.03, 0, -0.04, head_width=0.02, head_length=0.01, 
                    fc='black', ec='black')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('STGCN Architecture for Astana Traffic Forecasting', 
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('model_architecture.png', dpi=300, bbox_inches='tight')
    print("✅ Model architecture saved as 'model_architecture.png'")
    
    return fig

def create_results_summary():
    """Create a comprehensive results summary"""
    print("Creating results summary...")
    
    # Results data
    results = {
        'Dataset': ['Astana (Custom)', 'METR-LA (Benchmark)'],
        'Sensors': [100, 207],
        'Timesteps': [1000, 34272],
        'MAE': [1.619, 6.043],
        'RMSE': [2.018, 10.503],
        'WMAPE (%)': [5.51, 11.90],
        'Training Time (min)': [1, 50],
        'Model Size (MB)': [0.74, 0.95]
    }
    
    # Create summary table
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    for i in range(len(results['Dataset'])):
        row = [results[key][i] for key in results.keys()]
        table_data.append(row)
    
    table = ax.table(cellText=table_data,
                    colLabels=list(results.keys()),
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)
    
    # Color code the best performance
    for i in range(len(table_data)):
        for j in range(len(table_data[i])):
            if j >= 3 and j <= 5:  # MAE, RMSE, WMAPE columns
                if i == 0:  # Astana row
                    table[(i+1, j)].set_facecolor('#90EE90')  # Light green
                else:
                    table[(i+1, j)].set_facecolor('#FFB6C1')  # Light pink
    
    ax.set_title('STGCN Training Results Summary', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('results_summary.png', dpi=300, bbox_inches='tight')
    print("✅ Results summary saved as 'results_summary.png'")
    
    return fig

def main():
    """Create all visualizations"""
    print("🎨 Creating STGCN Results Visualizations...")
    print("=" * 50)
    
    try:
        # Create all visualizations
        create_training_plots()
        create_traffic_pattern_visualization()
        create_model_architecture_diagram()
        create_results_summary()
        
        print("\n" + "=" * 50)
        print("✅ ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
        print("=" * 50)
        print("\n📁 Generated Files:")
        print("   📊 training_results.png - Training progress plots")
        print("   🚗 traffic_patterns.png - Traffic pattern heatmaps")
        print("   🏗️  model_architecture.png - STGCN architecture diagram")
        print("   📋 results_summary.png - Performance comparison table")
        print("\n🎯 View these files to see your results!")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        print("Note: Some visualizations require matplotlib. Install with: pip install matplotlib")

if __name__ == "__main__":
    main()
