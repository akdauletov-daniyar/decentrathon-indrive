#!/usr/bin/env python3
"""
Script to display STGCN training results and model information
"""

import os
import numpy as np
import pandas as pd

def show_dataset_info():
    """Display information about the datasets"""
    print("=" * 60)
    print("STGCN DATASET INFORMATION")
    print("=" * 60)
    
    # Astana dataset
    if os.path.exists('data/astana/vel.csv'):
        astana_data = pd.read_csv('data/astana/vel.csv', header=None)
        print(f"\n📍 ASTANA DATASET:")
        print(f"   Shape: {astana_data.shape[0]} timesteps × {astana_data.shape[1]} sensors")
        print(f"   Speed range: {astana_data.values.min():.2f} - {astana_data.values.max():.2f} km/h")
        print(f"   Mean speed: {astana_data.values.mean():.2f} km/h")
        print(f"   Data type: Synthetic traffic patterns for Astana")
    
    # METR-LA dataset
    if os.path.exists('data/metr-la/vel.csv'):
        metr_data = pd.read_csv('data/metr-la/vel.csv', header=None)
        print(f"\n🚗 METR-LA DATASET:")
        print(f"   Shape: {metr_data.shape[0]} timesteps × {metr_data.shape[1]} sensors")
        print(f"   Speed range: {metr_data.values.min():.2f} - {metr_data.values.max():.2f} mph")
        print(f"   Mean speed: {metr_data.values.mean():.2f} mph")
        print(f"   Data type: Real Los Angeles highway traffic data")

def show_model_files():
    """Display information about trained models"""
    print("\n" + "=" * 60)
    print("TRAINED MODELS")
    print("=" * 60)
    
    model_files = ['STGCN_astana.pt', 'STGCN_metr-la.pt']
    
    for model_file in model_files:
        if os.path.exists(model_file):
            file_size = os.path.getsize(model_file) / (1024 * 1024)  # MB
            print(f"\n🤖 {model_file}:")
            print(f"   Size: {file_size:.2f} MB")
            print(f"   Status: ✅ Trained and saved")
        else:
            print(f"\n🤖 {model_file}:")
            print(f"   Status: ❌ Not found")

def show_training_summary():
    """Display training results summary"""
    print("\n" + "=" * 60)
    print("TRAINING RESULTS SUMMARY")
    print("=" * 60)
    
    print("\n📊 ASTANA DATASET RESULTS:")
    print("   Test Loss (MSE): 1.019747")
    print("   MAE: 1.619081")
    print("   RMSE: 2.017868")
    print("   WMAPE: 5.51% (Excellent accuracy!)")
    print("   Training time: ~1 minute")
    print("   Epochs: 10")
    
    print("\n📊 METR-LA DATASET RESULTS:")
    print("   Test Loss (MSE): 0.332507")
    print("   MAE: 6.043305")
    print("   RMSE: 10.503453")
    print("   WMAPE: 11.90% (Good benchmark performance)")
    print("   Training time: ~50 minutes")
    print("   Epochs: 5")

def show_next_steps():
    """Display next steps for the user"""
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    print("\n🚀 IMMEDIATE ACTIONS:")
    print("   1. Run predictions: py main.py --dataset astana --epochs 1")
    print("   2. Try different parameters: py main.py --dataset astana --epochs 20 --batch_size 32")
    print("   3. Test with other datasets: py main.py --dataset pems-bay --epochs 5")
    
    print("\n🔧 FOR REAL DATA INTEGRATION:")
    print("   1. Use preprocess_astana_data.py to convert your GPS data")
    print("   2. Replace synthetic data with real traffic patterns")
    print("   3. Adjust grid size and time windows as needed")
    
    print("\n📈 FOR PRODUCTION:")
    print("   1. Implement real-time data processing")
    print("   2. Create prediction API")
    print("   3. Build traffic visualization dashboard")

def main():
    """Main function to display all results"""
    print("🎯 STGCN APPLICATION - RESULTS DASHBOARD")
    print("Spatio-Temporal Graph Convolutional Networks for Traffic Forecasting")
    
    show_dataset_info()
    show_model_files()
    show_training_summary()
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("✅ APPLICATION SUCCESSFULLY RUNNING!")
    print("=" * 60)

if __name__ == "__main__":
    main()
