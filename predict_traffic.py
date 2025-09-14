#!/usr/bin/env python3
"""
Traffic Prediction and Heatmap Generation for STGCN
Creates 30-60 minute predictions with heatmap visualizations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_trained_model(dataset_name='astana'):
    """Load the trained STGCN model"""
    print(f"Loading trained model for {dataset_name}...")
    
    # Import required modules
    from model import models
    from script import dataloader, utility
    
    # Load adjacency matrix
    adj, n_vertex = dataloader.load_adj(dataset_name)
    gso = utility.calc_gso(adj, 'sym_norm_lap')
    gso = utility.calc_chebynet_gso(gso)
    gso = gso.toarray().astype(np.float32)
    gso = torch.from_numpy(gso)
    
    # Create model configuration
    class Args:
        def __init__(self):
            self.Kt = 3
            self.Ks = 3
            self.act_func = 'glu'
            self.graph_conv_type = 'cheb_graph_conv'
            self.gso = gso
            self.enable_bias = True
            self.droprate = 0.5
            self.n_his = 12
            self.n_pred = 3
    
    args = Args()
    blocks = [[1], [64, 16, 64], [64, 16, 64], [128, 128], [1]]
    
    # Create and load model
    if dataset_name == 'astana':
        model = models.STGCNChebGraphConv(args, blocks, n_vertex)
    else:
        model = models.STGCNGraphConv(args, blocks, n_vertex)
    
    # Load trained weights
    model_path = f"STGCN_{dataset_name}.pt"
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        print(f"✅ Model loaded from {model_path}")
    else:
        print(f"❌ Model file {model_path} not found!")
        return None, None, None
    
    model.eval()
    return model, n_vertex, gso

def prepare_prediction_data(dataset_name='astana', n_his=12):
    """Prepare the latest data for prediction"""
    print("Preparing prediction data...")
    
    # Load velocity data
    data_path = f'data/{dataset_name}/vel.csv'
    if not os.path.exists(data_path):
        print(f"❌ Data file {data_path} not found!")
        return None
    
    data = pd.read_csv(data_path, header=None)
    print(f"Loaded data shape: {data.shape}")
    
    # Get the last n_his timesteps for prediction
    recent_data = data.iloc[-n_his:].values
    print(f"Using last {n_his} timesteps for prediction")
    
    # Normalize the data (using the same scaler as training)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    recent_data_scaled = scaler.fit_transform(recent_data)
    
    # Reshape for model input: [1, 1, n_his, n_vertex]
    input_data = torch.FloatTensor(recent_data_scaled).unsqueeze(0).unsqueeze(0)
    
    return input_data, scaler, recent_data

def generate_predictions(model, input_data, n_vertex, prediction_steps=20):
    """Generate predictions for multiple time steps"""
    print(f"Generating predictions for {prediction_steps} steps...")
    
    predictions = []
    current_input = input_data.clone()
    
    with torch.no_grad():
        for step in range(prediction_steps):
            # Get prediction for next timestep
            pred = model(current_input)
            pred_reshaped = pred.view(1, 1, 1, n_vertex)
            
            # Store prediction
            predictions.append(pred_reshaped.squeeze().numpy())
            
            # Update input for next prediction (sliding window)
            current_input = torch.cat([
                current_input[:, :, 1:, :],  # Remove oldest timestep
                pred_reshaped  # Add new prediction
            ], dim=2)
    
    return np.array(predictions)

def create_traffic_heatmap(predictions, timestep, grid_size=10, title_suffix=""):
    """Create a traffic heatmap for a specific timestep"""
    
    # Reshape predictions to grid format
    if len(predictions.shape) == 1:
        # Single timestep - predictions is already 1D
        traffic_grid = predictions.reshape(grid_size, grid_size)
    else:
        # Multiple timesteps
        if timestep < len(predictions):
            traffic_grid = predictions[timestep].reshape(grid_size, grid_size)
        else:
            # If timestep is out of range, use the last available
            traffic_grid = predictions[-1].reshape(grid_size, grid_size)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(traffic_grid, cmap='YlOrRd', aspect='equal', 
                   vmin=traffic_grid.min(), vmax=traffic_grid.max())
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Traffic Speed (normalized)', rotation=270, labelpad=20)
    
    # Customize plot
    ax.set_title(f'Traffic Prediction Heatmap{title_suffix}', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Grid X Position', fontsize=12)
    ax.set_ylabel('Grid Y Position', fontsize=12)
    
    # Add grid lines
    ax.set_xticks(np.arange(-0.5, grid_size, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid_size, 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5, alpha=0.3)
    
    # Add text annotations for key areas
    for i in range(grid_size):
        for j in range(grid_size):
            text = ax.text(j, i, f'{traffic_grid[i, j]:.1f}',
                         ha="center", va="center", color="black", fontsize=8)
    
    plt.tight_layout()
    return fig

def create_prediction_timeline(predictions, grid_size=10, time_interval_minutes=5):
    """Create a timeline of predictions showing traffic evolution"""
    print("Creating prediction timeline...")
    
    n_predictions = len(predictions)
    cols = min(5, n_predictions)  # Max 5 columns
    rows = (n_predictions + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(20, 4*rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    
    for i in range(n_predictions):
        row = i // cols
        col = i % cols
        
        # Reshape prediction to grid
        traffic_grid = predictions[i].reshape(grid_size, grid_size)
        
        # Create subplot
        im = axes[row, col].imshow(traffic_grid, cmap='YlOrRd', aspect='equal')
        
        # Calculate time
        minutes_ahead = (i + 1) * time_interval_minutes
        
        axes[row, col].set_title(f'+{minutes_ahead} min', fontsize=12, fontweight='bold')
        axes[row, col].set_xticks([])
        axes[row, col].set_yticks([])
        
        # Add colorbar for each subplot
        plt.colorbar(im, ax=axes[row, col], shrink=0.6)
    
    # Hide empty subplots
    for i in range(n_predictions, rows * cols):
        row = i // cols
        col = i % cols
        axes[row, col].set_visible(False)
    
    plt.suptitle('Traffic Prediction Timeline (30-60 minutes ahead)', 
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    return fig

def create_3d_traffic_surface(predictions, timestep, grid_size=10):
    """Create a 3D surface plot of traffic patterns"""
    from mpl_toolkits.mplot3d import Axes3D
    
    # Reshape prediction to grid
    traffic_grid = predictions[timestep].reshape(grid_size, grid_size)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create coordinate grids
    x = np.arange(grid_size)
    y = np.arange(grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create 3D surface
    surf = ax.plot_surface(X, Y, traffic_grid, cmap='YlOrRd', 
                          alpha=0.8, linewidth=0, antialiased=True)
    
    # Customize plot
    ax.set_xlabel('Grid X Position')
    ax.set_ylabel('Grid Y Position')
    ax.set_zlabel('Traffic Speed (normalized)')
    ax.set_title(f'3D Traffic Surface - +{(timestep+1)*5} minutes ahead', 
                fontsize=14, fontweight='bold')
    
    # Add colorbar
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    return fig

def save_predictions_to_csv(predictions, scaler, output_file='traffic_predictions.csv'):
    """Save predictions to CSV file"""
    print(f"Saving predictions to {output_file}...")
    
    # Denormalize predictions
    predictions_denorm = scaler.inverse_transform(predictions)
    
    # Create DataFrame
    n_steps, n_sensors = predictions_denorm.shape
    columns = [f'Sensor_{i:03d}' for i in range(n_sensors)]
    
    df = pd.DataFrame(predictions_denorm, columns=columns)
    df.index.name = 'Prediction_Step'
    
    # Add time information
    current_time = datetime.now()
    df['Minutes_Ahead'] = [(i+1) * 5 for i in range(n_steps)]
    df['Prediction_Time'] = [current_time + timedelta(minutes=(i+1)*5) for i in range(n_steps)]
    
    # Reorder columns
    df = df[['Minutes_Ahead', 'Prediction_Time'] + columns]
    
    df.to_csv(output_file)
    print(f"✅ Predictions saved to {output_file}")
    
    return df

def main():
    """Main prediction function"""
    print("🚀 STGCN Traffic Prediction System")
    print("=" * 50)
    
    # Configuration
    dataset_name = 'astana'
    prediction_steps = 12  # 12 steps * 5 minutes = 60 minutes
    grid_size = 10  # 10x10 grid
    
    try:
        # Load trained model
        model, n_vertex, gso = load_trained_model(dataset_name)
        if model is None:
            return
        
        # Prepare prediction data
        input_data, scaler, recent_data = prepare_prediction_data(dataset_name)
        if input_data is None:
            return
        
        # Generate predictions
        predictions = generate_predictions(model, input_data, n_vertex, prediction_steps)
        print(f"✅ Generated {len(predictions)} prediction steps")
        
        # Create visualizations
        print("\n📊 Creating visualizations...")
        
        # 1. Current traffic heatmap (last known state)
        current_traffic = recent_data[-1]  # This is already 1D
        fig_current = create_traffic_heatmap(current_traffic, 0, grid_size, " - Current State")
        fig_current.savefig('current_traffic_heatmap.png', dpi=300, bbox_inches='tight')
        print("✅ Current traffic heatmap saved")
        
        # 2. Prediction timeline (30-60 minutes)
        fig_timeline = create_prediction_timeline(predictions, grid_size)
        fig_timeline.savefig('traffic_prediction_timeline.png', dpi=300, bbox_inches='tight')
        print("✅ Prediction timeline saved")
        
        # 3. Individual prediction heatmaps
        for i in [5, 11]:  # 30 and 60 minutes ahead
            minutes = (i + 1) * 5
            fig_pred = create_traffic_heatmap(predictions, i, grid_size, f" - +{minutes} minutes")
            fig_pred.savefig(f'traffic_prediction_{minutes}min.png', dpi=300, bbox_inches='tight')
            print(f"✅ {minutes}-minute prediction heatmap saved")
        
        # 4. 3D traffic surface (if matplotlib supports it)
        try:
            fig_3d = create_3d_traffic_surface(predictions, 5, grid_size)
            fig_3d.savefig('traffic_3d_surface.png', dpi=300, bbox_inches='tight')
            print("✅ 3D traffic surface saved")
        except Exception as e:
            print(f"⚠️ 3D visualization skipped: {e}")
        
        # 5. Save predictions to CSV
        df_predictions = save_predictions_to_csv(predictions, scaler)
        
        # Display summary
        print("\n" + "=" * 50)
        print("🎯 PREDICTION SUMMARY")
        print("=" * 50)
        print(f"📊 Generated predictions for {prediction_steps} time steps")
        print(f"⏰ Time horizon: 5-{prediction_steps*5} minutes ahead")
        print(f"🌍 Grid coverage: {grid_size}x{grid_size} locations")
        print(f"📈 Average predicted speed: {df_predictions.iloc[:, 2:].mean().mean():.2f} km/h")
        
        print("\n📁 Generated Files:")
        print("   🗺️  current_traffic_heatmap.png - Current traffic state")
        print("   📊 traffic_prediction_timeline.png - Full prediction timeline")
        print("   🔮 traffic_prediction_30min.png - 30-minute prediction")
        print("   🔮 traffic_prediction_60min.png - 60-minute prediction")
        print("   📈 traffic_3d_surface.png - 3D traffic surface")
        print("   📄 traffic_predictions.csv - Raw prediction data")
        
        print("\n✅ Traffic prediction complete!")
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
