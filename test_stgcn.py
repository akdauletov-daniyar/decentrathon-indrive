#!/usr/bin/env python3
"""
Simple test script to run STGCN with Astana dataset
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

try:
    print("Testing STGCN with Astana dataset...")
    
    # Test imports
    print("Testing imports...")
    import torch
    print("✓ PyTorch imported")
    
    import numpy as np
    print("✓ NumPy imported")
    
    import pandas as pd
    print("✓ Pandas imported")
    
    # Test data loading
    print("\nTesting data loading...")
    from script import dataloader
    
    adj, n_vertex = dataloader.load_adj('astana')
    print(f"✓ Adjacency matrix loaded: {adj.shape}, {n_vertex} vertices")
    
    train, val, test = dataloader.load_data('astana', 700, 150)
    print(f"✓ Data loaded: train={train.shape}, val={val.shape}, test={test.shape}")
    
    # Test model creation
    print("\nTesting model creation...")
    from model import models
    
    # Create simple args
    class Args:
        def __init__(self):
            self.Kt = 3
            self.Ks = 3
            self.act_func = 'glu'
            self.graph_conv_type = 'graph_conv'
            self.gso = torch.tensor(adj.toarray(), dtype=torch.float32)
            self.enable_bias = True
            self.droprate = 0.5
            self.n_his = 12
    
    args = Args()
    blocks = [[1], [64, 16, 64], [64, 16, 64], [128, 128], [1]]
    
    model = models.STGCNGraphConv(args, blocks, n_vertex)
    print(f"✓ Model created: {model}")
    
    print("\n=== All tests passed! ===")
    print("STGCN is ready to run with Astana dataset!")
    print("Run: python main.py --dataset astana --epochs 10")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages:")
    print("pip install torch pandas numpy scipy scikit-learn tqdm")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
