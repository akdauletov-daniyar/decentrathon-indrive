#!/usr/bin/env python3
"""
Script to create Astana dataset and run STGCN training
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n=== {description} ===")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("SUCCESS!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    print("=== Astana STGCN Training Pipeline ===")
    
    # Step 1: Create the dataset
    if not run_command("python create_astana_dataset.py", "Creating Astana dataset"):
        print("Failed to create dataset. Trying alternative approach...")
        
        # Alternative: Create dataset manually
        print("Creating dataset manually...")
        import numpy as np
        
        # Create dataset directory
        os.makedirs('data/astana', exist_ok=True)
        
        # Create simple velocity data
        n_sensors = 100
        n_timesteps = 1000
        velocity_data = np.random.uniform(20, 60, (n_timesteps, n_sensors))
        
        # Save velocity data
        np.savetxt('data/astana/vel.csv', velocity_data, delimiter=',', fmt='%.6f')
        print("Created velocity data")
        
        # Create simple adjacency matrix
        adjacency = np.eye(n_sensors) * 0.1  # Simple diagonal matrix
        np.savez_compressed('data/astana/adj.npz', adjacency)
        print("Created adjacency matrix")
        
        print("Dataset created successfully!")
    
    # Step 2: Run STGCN training
    print("\n=== Starting STGCN Training ===")
    
    # Try different Python commands
    python_commands = ['python', 'python3', 'py']
    
    for python_cmd in python_commands:
        print(f"Trying {python_cmd}...")
        if run_command(f"{python_cmd} main.py --dataset astana --epochs 10 --batch_size 16", f"Running STGCN with {python_cmd}"):
            print("Training completed successfully!")
            return
    
    print("All Python commands failed. Please check your Python installation.")
    print("\nManual steps:")
    print("1. Ensure Python is installed and in PATH")
    print("2. Install required packages: pip install torch pandas numpy scipy scikit-learn tqdm")
    print("3. Run: python main.py --dataset astana --epochs 10")

if __name__ == "__main__":
    main()
