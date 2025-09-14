import pandas as pd
import numpy as np
import os

print("Starting data preprocessing...")

# Load the GPS data
data_path = 'd:/Decentrathon/project1/datasets/geo_locations_astana_hackathon.txt'
print(f"Loading data from: {data_path}")

try:
    data = pd.read_csv(data_path)
    print(f"Successfully loaded {len(data)} records")
    print(f"Columns: {list(data.columns)}")
    
    # Show sample data
    print("\nSample data:")
    print(data.head())
    
    # Basic statistics
    print(f"\nSpeed statistics:")
    print(f"Min speed: {data['spd'].min()}")
    print(f"Max speed: {data['spd'].max()}")
    print(f"Mean speed: {data['spd'].mean()}")
    
    # Create a simple grid-based approach
    print("\nCreating spatial grid...")
    
    # Define grid bounds for Astana
    lat_min, lat_max = data['lat'].min(), data['lat'].max()
    lng_min, lng_max = data['lng'].min(), data['lng'].max()
    
    print(f"Latitude range: {lat_min:.6f} to {lat_max:.6f}")
    print(f"Longitude range: {lng_min:.6f} to {lng_max:.6f}")
    
    # Create a simple 10x10 grid
    grid_size = 10
    lat_step = (lat_max - lat_min) / grid_size
    lng_step = (lng_max - lng_min) / grid_size
    
    # Assign grid cells
    data['lat_grid'] = ((data['lat'] - lat_min) / lat_step).astype(int)
    data['lng_grid'] = ((data['lng'] - lng_min) / lng_step).astype(int)
    data['grid_id'] = data['lat_grid'] * grid_size + data['lng_grid']
    
    print(f"Created {grid_size}x{grid_size} grid ({grid_size*grid_size} cells)")
    
    # Count points per grid cell
    grid_counts = data['grid_id'].value_counts()
    print(f"Grid cells with data: {len(grid_counts)}")
    print(f"Max points per cell: {grid_counts.max()}")
    
    # Create time series (simplified - just use row order)
    print("\nCreating time series...")
    
    # Group by every 1000 records to create time windows
    time_window_size = 1000
    data['time_window'] = data.index // time_window_size
    
    # Aggregate by time window and grid
    aggregated = data.groupby(['time_window', 'grid_id'])['spd'].mean().reset_index()
    
    print(f"Created {len(aggregated['time_window'].unique())} time windows")
    print(f"Total aggregated observations: {len(aggregated)}")
    
    # Create velocity matrix
    print("\nCreating velocity matrix...")
    velocity_matrix = aggregated.pivot_table(
        index='time_window', 
        columns='grid_id', 
        values='spd', 
        fill_value=0.0
    )
    
    print(f"Velocity matrix shape: {velocity_matrix.shape}")
    
    # Create simple adjacency matrix (connect neighboring grid cells)
    print("\nCreating adjacency matrix...")
    n_cells = grid_size * grid_size
    adjacency = np.zeros((n_cells, n_cells))
    
    for i in range(grid_size):
        for j in range(grid_size):
            cell_id = i * grid_size + j
            
            # Connect to neighboring cells
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        neighbor_id = ni * grid_size + nj
                        adjacency[cell_id, neighbor_id] = 1.0
    
    # Remove self-loops
    np.fill_diagonal(adjacency, 0)
    
    print(f"Adjacency matrix shape: {adjacency.shape}")
    print(f"Non-zero connections: {np.sum(adjacency > 0)}")
    
    # Save dataset
    print("\nSaving dataset...")
    dataset_dir = 'data/astana'
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Save velocity data
    vel_file = os.path.join(dataset_dir, 'vel.csv')
    velocity_matrix.to_csv(vel_file, header=False, index=False)
    print(f"Saved velocity data to {vel_file}")
    
    # Save adjacency matrix
    adj_file = os.path.join(dataset_dir, 'adj.npz')
    np.savez_compressed(adj_file, adjacency)
    print(f"Saved adjacency matrix to {adj_file}")
    
    print("\n=== Preprocessing Complete ===")
    print(f"Dataset saved to: {dataset_dir}")
    print(f"Number of sensors: {n_cells}")
    print(f"Number of timesteps: {len(velocity_matrix)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
