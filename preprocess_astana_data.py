import pandas as pd
import numpy as np
import scipy.sparse as sp
from scipy.spatial.distance import pdist, squareform
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def create_spatial_grid(data, grid_size=0.01):
    """
    Create a spatial grid for Astana GPS data
    grid_size: degree units (approximately 1km for 0.01 degrees)
    """
    print("Creating spatial grid...")
    
    # Get bounds of the data
    lat_min, lat_max = data['lat'].min(), data['lat'].max()
    lng_min, lng_max = data['lng'].min(), data['lng'].max()
    
    print(f"Latitude range: {lat_min:.6f} to {lat_max:.6f}")
    print(f"Longitude range: {lng_min:.6f} to {lng_max:.6f}")
    
    # Create grid
    lat_bins = np.arange(lat_min, lat_max + grid_size, grid_size)
    lng_bins = np.arange(lng_min, lng_max + grid_size, grid_size)
    
    # Assign each point to a grid cell
    data['lat_bin'] = pd.cut(data['lat'], bins=lat_bins, labels=False, include_lowest=True)
    data['lng_bin'] = pd.cut(data['lng'], bins=lng_bins, labels=False, include_lowest=True)
    
    # Create grid cell IDs
    data['grid_id'] = data['lat_bin'] * len(lng_bins) + data['lng_bin']
    
    # Remove invalid grid cells
    data = data.dropna(subset=['grid_id'])
    data['grid_id'] = data['grid_id'].astype(int)
    
    # Get unique grid cells (virtual sensors)
    unique_grids = sorted(data['grid_id'].unique())
    n_sensors = len(unique_grids)
    
    print(f"Created {n_sensors} virtual sensors from {len(data)} GPS points")
    
    return data, unique_grids, n_sensors, lat_bins, lng_bins

def create_temporal_aggregation(data, time_window_minutes=5):
    """
    Aggregate data into regular time windows
    """
    print("Creating temporal aggregation...")
    
    # Convert to datetime if needed (assuming data is ordered by time)
    # Since we don't have explicit timestamps, we'll create them based on row order
    # assuming 1-second intervals between consecutive records
    data['timestamp'] = pd.date_range(
        start='2024-01-01 00:00:00', 
        periods=len(data), 
        freq='1S'
    )
    
    # Create time windows
    data['time_window'] = data['timestamp'].dt.floor(f'{time_window_minutes}min')
    
    # Group by time window and grid cell, aggregate speed
    aggregated = data.groupby(['time_window', 'grid_id'])['spd'].agg(['mean', 'count']).reset_index()
    
    # Rename columns
    aggregated.columns = ['time_window', 'grid_id', 'avg_speed', 'count']
    
    # Filter out grid cells with very few observations
    aggregated = aggregated[aggregated['count'] >= 2]
    
    print(f"Created {len(aggregated['time_window'].unique())} time windows")
    print(f"Total observations: {len(aggregated)}")
    
    return aggregated

def create_velocity_matrix(aggregated_data, unique_grids, n_sensors):
    """
    Create velocity matrix in STGCN format
    """
    print("Creating velocity matrix...")
    
    # Create pivot table: time windows x grid cells
    velocity_matrix = aggregated_data.pivot_table(
        index='time_window', 
        columns='grid_id', 
        values='avg_speed', 
        fill_value=0.0
    )
    
    # Ensure all grid cells are present
    for grid_id in unique_grids:
        if grid_id not in velocity_matrix.columns:
            velocity_matrix[grid_id] = 0.0
    
    # Reorder columns to match unique_grids order
    velocity_matrix = velocity_matrix.reindex(columns=unique_grids, fill_value=0.0)
    
    # Fill remaining NaN values with 0
    velocity_matrix = velocity_matrix.fillna(0.0)
    
    print(f"Velocity matrix shape: {velocity_matrix.shape}")
    print(f"Non-zero values: {(velocity_matrix > 0).sum().sum()}")
    
    return velocity_matrix

def create_adjacency_matrix(unique_grids, lat_bins, lng_bins, n_sensors):
    """
    Create adjacency matrix based on spatial proximity
    """
    print("Creating adjacency matrix...")
    
    # Calculate grid cell centers
    grid_centers = []
    for grid_id in unique_grids:
        lat_idx = grid_id // len(lng_bins)
        lng_idx = grid_id % len(lng_bins)
        
        lat_center = (lat_bins[lat_idx] + lat_bins[lat_idx + 1]) / 2
        lng_center = (lng_bins[lng_idx] + lng_bins[lng_idx + 1]) / 2
        
        grid_centers.append([lat_center, lng_center])
    
    grid_centers = np.array(grid_centers)
    
    # Calculate pairwise distances
    distances = pdist(grid_centers, metric='euclidean')
    distance_matrix = squareform(distances)
    
    # Create adjacency matrix based on distance threshold
    # Connect grid cells within a certain distance (e.g., 2 grid cells)
    threshold = 2 * 0.01  # 2 grid cells away
    adjacency = (distance_matrix <= threshold).astype(float)
    
    # Remove self-loops
    np.fill_diagonal(adjacency, 0)
    
    # Convert to sparse matrix
    adj_sparse = sp.csr_matrix(adjacency)
    
    print(f"Adjacency matrix shape: {adj_sparse.shape}")
    print(f"Non-zero connections: {adj_sparse.nnz}")
    print(f"Average connections per node: {adj_sparse.nnz / n_sensors:.2f}")
    
    return adj_sparse

def save_dataset(velocity_matrix, adjacency_matrix, n_sensors, dataset_name='astana'):
    """
    Save dataset in STGCN format
    """
    print("Saving dataset...")
    
    # Create dataset directory
    dataset_dir = f'data/{dataset_name}'
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Save velocity data as CSV (no headers, as expected by STGCN)
    vel_file = os.path.join(dataset_dir, 'vel.csv')
    velocity_matrix.to_csv(vel_file, header=False, index=False)
    print(f"Saved velocity data to {vel_file}")
    
    # Save adjacency matrix as NPZ
    adj_file = os.path.join(dataset_dir, 'adj.npz')
    sp.save_npz(adj_file, adjacency_matrix)
    print(f"Saved adjacency matrix to {adj_file}")
    
    # Save metadata
    metadata = {
        'n_sensors': n_sensors,
        'n_timesteps': len(velocity_matrix),
        'grid_size': 0.01,
        'time_window_minutes': 5
    }
    
    with open(os.path.join(dataset_dir, 'metadata.txt'), 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f"Dataset saved successfully!")
    print(f"Number of sensors: {n_sensors}")
    print(f"Number of timesteps: {len(velocity_matrix)}")
    
    return dataset_dir

def main():
    print("=== Astana GPS Data Preprocessing for STGCN ===")
    
    # Load the GPS data
    print("Loading GPS data...")
    data_path = 'd:/Decentrathon/project1/datasets/geo_locations_astana_hackathon.txt'
    data = pd.read_csv(data_path)
    
    print(f"Loaded {len(data)} GPS records")
    print(f"Columns: {list(data.columns)}")
    
    # Filter out invalid data
    data = data[data['spd'] >= 0]  # Remove negative speeds
    data = data[data['spd'] <= 200]  # Remove unrealistic speeds (>200 km/h)
    
    print(f"After filtering: {len(data)} records")
    
    # Step 1: Create spatial grid
    data, unique_grids, n_sensors, lat_bins, lng_bins = create_spatial_grid(data)
    
    # Step 2: Create temporal aggregation
    aggregated_data = create_temporal_aggregation(data)
    
    # Step 3: Create velocity matrix
    velocity_matrix = create_velocity_matrix(aggregated_data, unique_grids, n_sensors)
    
    # Step 4: Create adjacency matrix
    adjacency_matrix = create_adjacency_matrix(unique_grids, lat_bins, lng_bins, n_sensors)
    
    # Step 5: Save dataset
    dataset_dir = save_dataset(velocity_matrix, adjacency_matrix, n_sensors)
    
    print("\n=== Preprocessing Complete ===")
    print(f"Dataset saved to: {dataset_dir}")
    print("Ready for STGCN training!")

if __name__ == "__main__":
    main()
