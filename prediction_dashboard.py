#!/usr/bin/env python3
"""
Enhanced Prediction Dashboard for STGCN Traffic Forecasting
Shows real-time predictions and heatmap layers
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

def create_enhanced_prediction_dashboard():
    """Create a comprehensive prediction dashboard"""
    print("🎯 Creating Enhanced Prediction Dashboard...")
    
    # Load prediction data
    if not os.path.exists('traffic_predictions.csv'):
        print("❌ Prediction data not found. Run predict_traffic.py first.")
        return
    
    df = pd.read_csv('traffic_predictions.csv', index_col=0)
    
    # Create comprehensive dashboard
    fig = plt.figure(figsize=(20, 16))
    
    # Main title
    fig.suptitle('STGCN Traffic Prediction Dashboard - Astana City', 
                fontsize=20, fontweight='bold', y=0.95)
    
    # 1. Current Traffic State (Top Left)
    ax1 = plt.subplot(3, 4, 1)
    if os.path.exists('current_traffic_heatmap.png'):
        img1 = plt.imread('current_traffic_heatmap.png')
        ax1.imshow(img1)
        ax1.set_title('Current Traffic State', fontsize=14, fontweight='bold')
        ax1.axis('off')
    else:
        ax1.text(0.5, 0.5, 'Current State\nNot Available', 
                ha='center', va='center', fontsize=12)
        ax1.set_title('Current Traffic State', fontsize=14, fontweight='bold')
    
    # 2. 30-Minute Prediction (Top Center)
    ax2 = plt.subplot(3, 4, 2)
    if os.path.exists('traffic_prediction_30min.png'):
        img2 = plt.imread('traffic_prediction_30min.png')
        ax2.imshow(img2)
        ax2.set_title('30-Minute Prediction', fontsize=14, fontweight='bold')
        ax2.axis('off')
    else:
        ax2.text(0.5, 0.5, '30-Min Prediction\nNot Available', 
                ha='center', va='center', fontsize=12)
        ax2.set_title('30-Minute Prediction', fontsize=14, fontweight='bold')
    
    # 3. 60-Minute Prediction (Top Right)
    ax3 = plt.subplot(3, 4, 3)
    if os.path.exists('traffic_prediction_60min.png'):
        img3 = plt.imread('traffic_prediction_60min.png')
        ax3.imshow(img3)
        ax3.set_title('60-Minute Prediction', fontsize=14, fontweight='bold')
        ax3.axis('off')
    else:
        ax3.text(0.5, 0.5, '60-Min Prediction\nNot Available', 
                ha='center', va='center', fontsize=12)
        ax3.set_title('60-Minute Prediction', fontsize=14, fontweight='bold')
    
    # 4. Prediction Timeline (Top Right)
    ax4 = plt.subplot(3, 4, 4)
    if os.path.exists('traffic_prediction_timeline.png'):
        img4 = plt.imread('traffic_prediction_timeline.png')
        ax4.imshow(img4)
        ax4.set_title('Prediction Timeline', fontsize=14, fontweight='bold')
        ax4.axis('off')
    else:
        ax4.text(0.5, 0.5, 'Timeline\nNot Available', 
                ha='center', va='center', fontsize=12)
        ax4.set_title('Prediction Timeline', fontsize=14, fontweight='bold')
    
    # 5. Speed Distribution (Middle Left)
    ax5 = plt.subplot(3, 4, 5)
    sensor_data = df.iloc[:, 2:].values  # All sensor data
    ax5.hist(sensor_data.flatten(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax5.set_title('Speed Distribution', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Speed (km/h)')
    ax5.set_ylabel('Frequency')
    ax5.grid(True, alpha=0.3)
    
    # 6. Average Speed Over Time (Middle Center)
    ax6 = plt.subplot(3, 4, 6)
    avg_speeds = df.iloc[:, 2:].mean(axis=1)
    minutes_ahead = df['Minutes_Ahead'].values
    ax6.plot(minutes_ahead, avg_speeds, 'b-o', linewidth=2, markersize=6)
    ax6.set_title('Average Speed Over Time', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Minutes Ahead')
    ax6.set_ylabel('Average Speed (km/h)')
    ax6.grid(True, alpha=0.3)
    
    # 7. Speed Statistics (Middle Right)
    ax7 = plt.subplot(3, 4, 7)
    stats_data = [
        ['Min Speed', f'{sensor_data.min():.1f} km/h'],
        ['Max Speed', f'{sensor_data.max():.1f} km/h'],
        ['Avg Speed', f'{sensor_data.mean():.1f} km/h'],
        ['Std Dev', f'{sensor_data.std():.1f} km/h'],
        ['Predictions', f'{len(df)} steps'],
        ['Sensors', '100 (10x10 grid)']
    ]
    
    ax7.axis('off')
    table = ax7.table(cellText=stats_data, 
                     colLabels=['Metric', 'Value'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax7.set_title('Prediction Statistics', fontsize=12, fontweight='bold')
    
    # 8. Traffic Congestion Map (Bottom Left)
    ax8 = plt.subplot(3, 4, 9)
    
    # Calculate congestion levels (inverse of speed)
    congestion_data = df.iloc[:, 2:].values
    congestion_levels = 1 / (congestion_data + 1)  # Avoid division by zero
    avg_congestion = congestion_levels.mean(axis=0).reshape(10, 10)
    
    im8 = ax8.imshow(avg_congestion, cmap='Reds', aspect='equal')
    ax8.set_title('Average Congestion Level', fontsize=12, fontweight='bold')
    ax8.set_xlabel('Grid X')
    ax8.set_ylabel('Grid Y')
    plt.colorbar(im8, ax=ax8, shrink=0.8)
    
    # 9. Prediction Accuracy (Bottom Center)
    ax9 = plt.subplot(3, 4, 10)
    
    # Simulate prediction confidence (based on variance)
    prediction_variance = df.iloc[:, 2:].var(axis=1)
    confidence = 1 / (1 + prediction_variance)  # Higher variance = lower confidence
    
    ax9.plot(minutes_ahead, confidence, 'g-o', linewidth=2, markersize=6)
    ax9.set_title('Prediction Confidence', fontsize=12, fontweight='bold')
    ax9.set_xlabel('Minutes Ahead')
    ax9.set_ylabel('Confidence Score')
    ax9.grid(True, alpha=0.3)
    ax9.set_ylim(0, 1)
    
    # 10. Time Information (Bottom Right)
    ax10 = plt.subplot(3, 4, 11)
    current_time = datetime.now()
    
    time_info = [
        ['Current Time', current_time.strftime('%H:%M:%S')],
        ['Prediction Start', current_time.strftime('%H:%M:%S')],
        ['Prediction End', (current_time + timedelta(minutes=60)).strftime('%H:%M:%S')],
        ['Time Horizon', '60 minutes'],
        ['Update Interval', '5 minutes'],
        ['Grid Resolution', '10x10 cells']
    ]
    
    ax10.axis('off')
    table2 = ax10.table(cellText=time_info,
                       colLabels=['Parameter', 'Value'],
                       cellLoc='center',
                       loc='center',
                       bbox=[0, 0, 1, 1])
    table2.auto_set_font_size(False)
    table2.set_fontsize(10)
    table2.scale(1, 2)
    ax10.set_title('System Information', fontsize=12, fontweight='bold')
    
    # 11. 3D Surface (Bottom Right)
    ax11 = plt.subplot(3, 4, 12)
    if os.path.exists('traffic_3d_surface.png'):
        img11 = plt.imread('traffic_3d_surface.png')
        ax11.imshow(img11)
        ax11.set_title('3D Traffic Surface', fontsize=12, fontweight='bold')
        ax11.axis('off')
    else:
        ax11.text(0.5, 0.5, '3D Surface\nNot Available', 
                ha='center', va='center', fontsize=12)
        ax11.set_title('3D Traffic Surface', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('enhanced_prediction_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Enhanced prediction dashboard saved as 'enhanced_prediction_dashboard.png'")
    
    return fig

def create_prediction_summary():
    """Create a text summary of predictions"""
    if not os.path.exists('traffic_predictions.csv'):
        print("❌ Prediction data not found.")
        return
    
    df = pd.read_csv('traffic_predictions.csv', index_col=0)
    
    print("\n" + "="*60)
    print("🎯 TRAFFIC PREDICTION SUMMARY")
    print("="*60)
    
    print(f"📅 Prediction Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Time Horizon: 5-{df['Minutes_Ahead'].max()} minutes ahead")
    print(f"🌍 Coverage: {df.shape[1]-2} sensors in 10x10 grid")
    print(f"📊 Predictions: {len(df)} time steps")
    
    sensor_data = df.iloc[:, 2:].values
    print(f"\n📈 Speed Statistics:")
    print(f"   Min Speed: {sensor_data.min():.2f} km/h")
    print(f"   Max Speed: {sensor_data.max():.2f} km/h")
    print(f"   Average Speed: {sensor_data.mean():.2f} km/h")
    print(f"   Standard Deviation: {sensor_data.std():.2f} km/h")
    
    print(f"\n🔮 Key Predictions:")
    for i in [0, 5, 11]:  # 5, 30, 60 minutes
        if i < len(df):
            minutes = df.iloc[i]['Minutes_Ahead']
            avg_speed = df.iloc[i, 2:].mean()
            print(f"   +{minutes:2d} min: {avg_speed:.2f} km/h average")
    
    print(f"\n📁 Generated Files:")
    files = [
        'current_traffic_heatmap.png',
        'traffic_prediction_timeline.png', 
        'traffic_prediction_30min.png',
        'traffic_prediction_60min.png',
        'traffic_3d_surface.png',
        'enhanced_prediction_dashboard.png',
        'traffic_predictions.csv'
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            print(f"   ✅ {file} ({size:.1f} KB)")
        else:
            print(f"   ❌ {file} (not found)")

def main():
    """Main function"""
    print("🚀 Enhanced Prediction Dashboard")
    print("="*50)
    
    try:
        # Create enhanced dashboard
        create_enhanced_prediction_dashboard()
        
        # Create summary
        create_prediction_summary()
        
        print("\n✅ Enhanced prediction dashboard complete!")
        print("🎯 View 'enhanced_prediction_dashboard.png' for full visualization")
        
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
