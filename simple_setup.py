# Simple setup script that creates the required files
import os

# Create data directory
os.makedirs('data/astana', exist_ok=True)

# Create a simple velocity CSV file
print("Creating velocity data...")
with open('data/astana/vel.csv', 'w') as f:
    for t in range(1000):  # 1000 timesteps
        row = []
        for s in range(100):  # 100 sensors
            # Create some realistic speed values
            speed = 30 + (t % 24) * 2 + (s % 10) * 1.5
            row.append(f"{speed:.2f}")
        f.write(','.join(row) + '\n')

print("Velocity data created!")

# Create a simple adjacency matrix
print("Creating adjacency matrix...")
adj_data = []
for i in range(100):
    row = []
    for j in range(100):
        if i == j:
            row.append(0.0)
        elif abs(i - j) == 1 or abs(i - j) == 10:  # Simple connectivity
            row.append(0.1)
        else:
            row.append(0.0)
    adj_data.append(row)

# Save as simple text file first
with open('data/astana/adj.txt', 'w') as f:
    for row in adj_data:
        f.write(','.join(map(str, row)) + '\n')

print("Adjacency matrix created!")
print("Dataset setup complete!")
print("Files created:")
print("- data/astana/vel.csv")
print("- data/astana/adj.txt")
