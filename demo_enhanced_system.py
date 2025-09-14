#!/usr/bin/env python3
"""
Demo script for Enhanced Hot Spot Detection System
Shows the system capabilities with sample data
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def create_demo_data():
    """Create demo data for testing"""
    print("🎭 Creating demo data...")
    
    # Create demo traffic data
    np.random.seed(42)
    n_timesteps = 1000
    n_sensors = 100
    
    # Generate realistic traffic patterns
    traffic_data = np.zeros((n_timesteps, n_sensors))
    
    for t in range(n_timesteps):
        # Simulate daily patterns
        hour = (t % 24) * 0.1
        
        # Rush hour patterns
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            base_speed = 20 + np.random.normal(0, 5)
        else:
            base_speed = 40 + np.random.normal(0, 10)
        
        # Add spatial variation
        for s in range(n_sensors):
            spatial_factor = 0.8 + 0.4 * (s % 10) / 10
            traffic_data[t, s] = max(0, base_speed * spatial_factor + np.random.normal(0, 3))
    
    # Create data directory
    os.makedirs('data/astana', exist_ok=True)
    
    # Save velocity data
    vel_file = 'data/astana/vel.csv'
    np.savetxt(vel_file, traffic_data, delimiter=',', fmt='%.6f')
    print(f"   ✅ Created {vel_file}")
    
    # Create adjacency matrix
    adjacency = np.zeros((n_sensors, n_sensors))
    grid_size = 10
    
    for i in range(grid_size):
        for j in range(grid_size):
            sensor_id = i * grid_size + j
            
            # Connect to 8 neighboring cells
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        neighbor_id = ni * grid_size + nj
                        distance = np.sqrt(di*di + dj*dj)
                        weight = 1.0 / distance if distance > 0 else 0
                        adjacency[sensor_id, neighbor_id] = weight
    
    # Normalize adjacency matrix
    for i in range(n_sensors):
        row_sum = adjacency[i].sum()
        if row_sum > 0:
            adjacency[i] = adjacency[i] / row_sum
    
    # Save adjacency matrix
    adj_file = 'data/astana/adj.npz'
    np.savez_compressed(adj_file, adjacency)
    print(f"   ✅ Created {adj_file}")
    
    return True

def create_demo_model():
    """Create a demo trained model"""
    print("🤖 Creating demo model...")
    
    try:
        from model import models
        from script import dataloader, utility
        import torch
        
        # Load adjacency matrix
        adj, n_vertex = dataloader.load_adj('astana')
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
        
        # Create model
        model = models.STGCNChebGraphConv(args, blocks, n_vertex)
        
        # Initialize with random weights (for demo purposes)
        for param in model.parameters():
            param.data.normal_(0, 0.1)
        
        # Save model
        model_path = 'STGCN_astana.pt'
        torch.save(model.state_dict(), model_path)
        print(f"   ✅ Created {model_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create demo model: {e}")
        return False

def run_demo():
    """Run the enhanced detection demo"""
    print("🚀 Running Enhanced Hot Spot Detection Demo")
    print("=" * 60)
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        # Initialize detector
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        
        # Set demo mode (no API keys)
        detector.set_api_keys(twogis_key=None, openai_key=None)
        
        # Run detection
        print("\n📊 Running detection pipeline...")
        success = detector.run_enhanced_detection()
        
        if success:
            print("\n✅ Demo completed successfully!")
            return True
        else:
            print("\n❌ Demo failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_results():
    """Display demo results"""
    print("\n📁 Demo Results:")
    print("-" * 40)
    
    files_to_check = [
        ('current_hotspots.html', 'Current hot spots visualization'),
        ('predicted_hotspots_30min.html', '30-minute predictions'),
        ('current_tile_heatmap.csv', 'Current tile heat levels'),
        ('predicted_tile_heatmap_30min.csv', 'Predicted tile heat levels')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename) / 1024  # KB
            print(f"   ✅ {filename} ({size:.1f} KB) - {description}")
        else:
            print(f"   ❌ {filename} - NOT FOUND")
    
    print("\n🌐 Open the HTML files in your browser to view the visualizations!")
    print("📊 The CSV files contain tile-based heat level data for analysis.")

def main():
    """Main demo function"""
    print("🎭 Enhanced Hot Spot Detection System - Demo")
    print("=" * 60)
    print("This demo will create sample data and run the enhanced detection system.")
    print("No API keys required - the system will use mock data.")
    print()
    
    # Check if data already exists
    if os.path.exists('data/astana/vel.csv') and os.path.exists('STGCN_astana.pt'):
        print("📁 Data files already exist, skipping creation...")
    else:
        # Create demo data
        if not create_demo_data():
            print("❌ Failed to create demo data")
            return False
        
        # Create demo model
        if not create_demo_model():
            print("❌ Failed to create demo model")
            return False
    
    # Run demo
    if not run_demo():
        print("❌ Demo failed")
        return False
    
    # Show results
    show_results()
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📚 Next Steps:")
    print("   1. Open the HTML files in your browser")
    print("   2. Examine the CSV files for data analysis")
    print("   3. Set up API keys for real-world data")
    print("   4. Run 'python run_enhanced_detection.py' for full system")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
