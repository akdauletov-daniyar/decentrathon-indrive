# Create simple data files for Astana dataset
import os

# Create data directory
os.makedirs('data/astana', exist_ok=True)

# Create simple velocity data (1000 timesteps, 100 sensors)
print("Creating velocity data...")
with open('data/astana/vel.csv', 'w') as f:
    for t in range(1000):
        row = []
        for s in range(100):
            # Create some pattern: base speed + time variation + sensor variation
            speed = 30 + (t % 24) * 2 + (s % 10) * 1.5
            row.append(f"{speed:.2f}")
        f.write(','.join(row) + '\n')

print("Velocity data created: 1000 timesteps x 100 sensors")
print("Files created:")
print("- data/astana/vel.csv")
print("Ready to run STGCN!")
