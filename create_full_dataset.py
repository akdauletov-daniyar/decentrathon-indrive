import numpy as np
import os

# Create a proper dataset for STGCN
print("Creating full Astana dataset...")

# Create data directory
os.makedirs('data/astana', exist_ok=True)

# Create velocity data (1000 timesteps, 100 sensors)
n_timesteps = 1000
n_sensors = 100

print(f"Creating {n_timesteps} timesteps x {n_sensors} sensors...")

with open('data/astana/vel.csv', 'w') as f:
    for t in range(n_timesteps):
        row = []
        for s in range(n_sensors):
            # Create realistic traffic patterns
            # Base speed with time variation (rush hours) and spatial variation
            base_speed = 30.0
            
            # Time variation (rush hours at 7-9 AM and 5-7 PM)
            hour = (t % 24) * 0.1  # Convert to hour-like pattern
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                time_factor = 0.7  # Slower during rush hour
            else:
                time_factor = 1.0  # Normal speed
            
            # Spatial variation (different areas have different speeds)
            spatial_factor = 0.8 + 0.4 * (s % 10) / 10
            
            # Add some noise
            noise = np.random.normal(0, 2)
            
            speed = base_speed * time_factor * spatial_factor + noise
            speed = max(0, speed)  # Ensure non-negative
            
            row.append(f"{speed:.2f}")
        f.write(','.join(row) + '\n')

print(f"Created velocity data: {n_timesteps} timesteps x {n_sensors} sensors")

# Create adjacency matrix
print("Creating adjacency matrix...")
adjacency = np.zeros((n_sensors, n_sensors))
grid_size = 10

# Create 10x10 grid connectivity
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

# Save adjacency matrix
np.savez_compressed('data/astana/adj.npz', adjacency)

print(f"Created adjacency matrix: {adjacency.shape}")
print(f"Non-zero connections: {np.sum(adjacency > 0)}")

print("\n=== Dataset Creation Complete ===")
print(f"Files created:")
print(f"- data/astana/vel.csv ({n_timesteps} rows x {n_sensors} columns)")
print(f"- data/astana/adj.npz ({n_sensors}x{n_sensors} matrix)")
print("Ready for STGCN training!")
