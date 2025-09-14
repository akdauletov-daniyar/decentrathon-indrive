import numpy as np
import os

# Create a simple synthetic dataset based on the Astana GPS data characteristics
print("Creating Astana synthetic dataset...")

# Based on the GPS data, create a 10x10 grid (100 sensors)
n_sensors = 100
n_timesteps = 1000

# Create synthetic velocity data with some realistic patterns
np.random.seed(42)

# Create base velocity pattern (simulating traffic patterns)
velocity_data = np.zeros((n_timesteps, n_sensors))

# Add some temporal patterns (rush hours, etc.)
for t in range(n_timesteps):
    # Simulate daily pattern
    hour = (t % 24) * 0.1  # Convert to hour-like pattern
    
    # Rush hour pattern
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        base_speed = 20 + np.random.normal(0, 5)  # Slower during rush hour
    else:
        base_speed = 40 + np.random.normal(0, 10)  # Normal speed
    
    # Add spatial variation (some areas are always slower)
    for s in range(n_sensors):
        spatial_factor = 0.8 + 0.4 * (s % 10) / 10  # Vary by grid position
        velocity_data[t, s] = max(0, base_speed * spatial_factor + np.random.normal(0, 3))

# Create adjacency matrix (10x10 grid with 8-connected neighbors)
adjacency = np.zeros((n_sensors, n_sensors))
grid_size = 10

for i in range(grid_size):
    for j in range(grid_size):
        sensor_id = i * grid_size + j
        
        # Connect to 8 neighboring cells
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue  # Skip self
                
                ni, nj = i + di, j + dj
                if 0 <= ni < grid_size and 0 <= nj < grid_size:
                    neighbor_id = ni * grid_size + nj
                    # Use distance-based weights
                    distance = np.sqrt(di*di + dj*dj)
                    weight = 1.0 / distance if distance > 0 else 0
                    adjacency[sensor_id, neighbor_id] = weight

# Normalize adjacency matrix
for i in range(n_sensors):
    row_sum = adjacency[i].sum()
    if row_sum > 0:
        adjacency[i] = adjacency[i] / row_sum

print(f"Created dataset with {n_sensors} sensors and {n_timesteps} timesteps")
print(f"Velocity data shape: {velocity_data.shape}")
print(f"Adjacency matrix shape: {adjacency.shape}")
print(f"Non-zero connections: {np.sum(adjacency > 0)}")

# Create dataset directory
dataset_dir = 'data/astana'
os.makedirs(dataset_dir, exist_ok=True)

# Save velocity data as CSV (no headers, as expected by STGCN)
vel_file = os.path.join(dataset_dir, 'vel.csv')
np.savetxt(vel_file, velocity_data, delimiter=',', fmt='%.6f')
print(f"Saved velocity data to {vel_file}")

# Save adjacency matrix as NPZ
adj_file = os.path.join(dataset_dir, 'adj.npz')
np.savez_compressed(adj_file, adjacency)
print(f"Saved adjacency matrix to {adj_file}")

# Create a simple metadata file
metadata_file = os.path.join(dataset_dir, 'metadata.txt')
with open(metadata_file, 'w') as f:
    f.write(f"n_sensors: {n_sensors}\n")
    f.write(f"n_timesteps: {n_timesteps}\n")
    f.write(f"grid_size: 10x10\n")
    f.write(f"description: Synthetic Astana traffic dataset\n")

print(f"Saved metadata to {metadata_file}")
print("Dataset creation complete!")
