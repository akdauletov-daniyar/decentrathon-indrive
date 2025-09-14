import numpy as np

# Create adjacency matrix for Astana dataset
n_sensors = 100
grid_size = 10

# Create 10x10 grid adjacency matrix
adjacency = np.zeros((n_sensors, n_sensors))

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

print(f"Created adjacency matrix with shape: {adjacency.shape}")
print(f"Non-zero connections: {np.sum(adjacency > 0)}")
print("Saved to data/astana/adj.npz")
