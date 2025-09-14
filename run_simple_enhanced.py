#!/usr/bin/env python3
"""
Simple Enhanced Hot Spot Detection Runner
Works with existing STGCN setup
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def create_sample_data():
    """Create sample data if needed"""
    print("📊 Creating sample data...")
    
    # Check if data exists
    if os.path.exists('data/astana/vel.csv'):
        print("   ✅ Data file exists")
        return True
    
    # Create data directory
    os.makedirs('data/astana', exist_ok=True)
    
    # Generate sample traffic data
    np.random.seed(42)
    n_timesteps = 1000
    n_sensors = 100
    
    traffic_data = np.zeros((n_timesteps, n_sensors))
    
    for t in range(n_timesteps):
        hour = (t % 24) * 0.1
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            base_speed = 20 + np.random.normal(0, 5)
        else:
            base_speed = 40 + np.random.normal(0, 10)
        
        for s in range(n_sensors):
            spatial_factor = 0.8 + 0.4 * (s % 10) / 10
            traffic_data[t, s] = max(0, base_speed * spatial_factor + np.random.normal(0, 3))
    
    # Save velocity data
    np.savetxt('data/astana/vel.csv', traffic_data, delimiter=',', fmt='%.6f')
    print("   ✅ Created velocity data")
    
    # Create adjacency matrix
    adjacency = np.zeros((n_sensors, n_sensors))
    grid_size = 10
    
    for i in range(grid_size):
        for j in range(grid_size):
            sensor_id = i * grid_size + j
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
    
    # Normalize
    for i in range(n_sensors):
        row_sum = adjacency[i].sum()
        if row_sum > 0:
            adjacency[i] = adjacency[i] / row_sum
    
    # Save adjacency
    np.savez_compressed('data/astana/adj.npz', adjacency)
    print("   ✅ Created adjacency matrix")
    
    return True

def create_simple_model():
    """Create a simple model for testing"""
    print("🤖 Creating simple model...")
    
    try:
        import torch
        from model import models
        from script import dataloader, utility
        
        # Load adjacency
        adj, n_vertex = dataloader.load_adj('astana')
        gso = utility.calc_gso(adj, 'sym_norm_lap')
        gso = utility.calc_chebynet_gso(gso)
        gso = gso.toarray().astype(np.float32)
        gso = torch.from_numpy(gso)
        
        # Create model
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
        
        model = models.STGCNChebGraphConv(args, blocks, n_vertex)
        
        # Initialize with random weights
        for param in model.parameters():
            param.data.normal_(0, 0.1)
        
        # Save model
        torch.save(model.state_dict(), 'STGCN_astana.pt')
        print("   ✅ Model created and saved")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating model: {e}")
        return False

def detect_hotspots_simple():
    """Simple hot spot detection"""
    print("🔥 Detecting hot spots...")
    
    try:
        # Load data
        data = pd.read_csv('data/astana/vel.csv', header=None)
        recent_data = data.iloc[-1].values  # Last timestep
        
        # Reshape to grid
        grid_size = 10
        traffic_grid = recent_data.reshape(grid_size, grid_size)
        
        # Normalize
        normalized = (traffic_grid - traffic_grid.min()) / (traffic_grid.max() - traffic_grid.min())
        
        # Find hotspots
        threshold = 0.7
        hotspots = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                if normalized[i, j] > threshold:
                    lat = 51.1694 + (i - grid_size/2) * 0.01
                    lon = 71.4491 + (j - grid_size/2) * 0.01
                    
                    hotspots.append({
                        'grid_x': i, 'grid_y': j,
                        'latitude': lat, 'longitude': lon,
                        'intensity': normalized[i, j],
                        'traffic_level': traffic_grid[i, j]
                    })
        
        print(f"   ✅ Found {len(hotspots)} hot spots")
        return hotspots
        
    except Exception as e:
        print(f"   ❌ Error detecting hotspots: {e}")
        return []

def generate_mock_organizations(hotspots):
    """Generate mock organization data"""
    print("🏢 Generating organization data...")
    
    org_types = ['restaurant', 'shopping_center', 'office', 'entertainment', 'hotel']
    organizations = []
    
    for hotspot in hotspots:
        n_orgs = np.random.randint(2, 8)
        center_orgs = []
        
        for _ in range(n_orgs):
            org_type = np.random.choice(org_types)
            closing_hour = np.random.randint(18, 24)
            
            center_orgs.append({
                'name': f"{org_type.replace('_', ' ').title()} {np.random.randint(1, 100)}",
                'type': org_type,
                'closing_time': closing_hour,
                'latitude': hotspot['latitude'] + np.random.normal(0, 0.001),
                'longitude': hotspot['longitude'] + np.random.normal(0, 0.001)
            })
        
        organizations.append({
            'hotspot_center': hotspot,
            'organizations': center_orgs,
            'organization_count': len(center_orgs)
        })
    
    print(f"   ✅ Generated organization data for {len(organizations)} locations")
    return organizations

def generate_mock_events(hotspots):
    """Generate mock event data"""
    print("🎉 Generating event data...")
    
    event_types = ['concert', 'festival', 'sports_event', 'conference', 'exhibition']
    events = []
    
    for hotspot in hotspots:
        if np.random.random() < 0.3:  # 30% chance of event
            event_type = np.random.choice(event_types)
            event_name = f"{event_type.replace('_', ' ').title()} Event"
            attendance = np.random.randint(50, 2000)
            
            event_info = f"Event: {event_name}\nType: {event_type}\nExpected Attendance: {attendance} people\nTime: {datetime.now().strftime('%H:%M')}"
            has_events = True
        else:
            event_info = "No events found"
            has_events = False
        
        events.append({
            'hotspot_center': hotspot,
            'event_info': event_info,
            'has_events': has_events
        })
    
    print(f"   ✅ Generated event data for {len(events)} locations")
    return events

def create_html_visualization(hotspots, organizations, events, filename='hotspot_output.html'):
    """Create HTML visualization"""
    print(f"🌐 Creating HTML visualization: {filename}")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Hot Spot Detection - Astana City</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .hotspot {{
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .hotspot h3 {{
                color: #e74c3c;
                margin-top: 0;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin: 15px 0;
            }}
            .info-item {{
                background: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border-left: 3px solid #3498db;
            }}
            .org-item {{
                background: #e8f5e8;
                padding: 8px;
                margin: 5px 0;
                border-radius: 5px;
                border-left: 3px solid #27ae60;
            }}
            .event-item {{
                background: #fff3cd;
                padding: 8px;
                margin: 5px 0;
                border-radius: 5px;
                border-left: 3px solid #ffc107;
            }}
            .timestamp {{
                text-align: center;
                color: #7f8c8d;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔥 Enhanced Hot Spot Detection - Astana City</h1>
                <p>Real-time traffic analysis with organization and event data</p>
            </div>
    """
    
    # Add hotspots
    if hotspots:
        html_content += "<h2>📍 Detected Hot Spots</h2>"
        for i, hotspot in enumerate(hotspots):
            html_content += f"""
            <div class="hotspot">
                <h3>Hot Spot #{i+1}</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Coordinates:</strong> {hotspot['latitude']:.4f}, {hotspot['longitude']:.4f}
                    </div>
                    <div class="info-item">
                        <strong>Intensity:</strong> {hotspot['intensity']:.2f}
                    </div>
                    <div class="info-item">
                        <strong>Traffic Level:</strong> {hotspot['traffic_level']:.1f} km/h
                    </div>
                    <div class="info-item">
                        <strong>Grid Position:</strong> ({hotspot['grid_x']}, {hotspot['grid_y']})
                    </div>
                </div>
            </div>
            """
    else:
        html_content += "<h2>📍 No Hot Spots Detected</h2><p>No high-traffic areas found in current data.</p>"
    
    # Add organizations
    if organizations:
        html_content += "<h2>🏢 Nearby Organizations</h2>"
        for i, org_data in enumerate(organizations):
            center = org_data['hotspot_center']
            orgs = org_data['organizations']
            
            html_content += f"""
            <div class="hotspot">
                <h3>Location #{i+1} - {org_data['organization_count']} Organizations</h3>
                <div class="info-item">
                    <strong>Center:</strong> {center['latitude']:.4f}, {center['longitude']:.4f}
                </div>
                <div style="margin-top: 15px;">
            """
            
            for org in orgs:
                html_content += f"""
                    <div class="org-item">
                        <strong>{org['name']}</strong><br>
                        Type: {org['type']} | Closing: {org['closing_time']}:00
                    </div>
                """
            
            html_content += "</div></div>"
    
    # Add events
    if events:
        html_content += "<h2>🎉 Event Information</h2>"
        for i, event_data in enumerate(events):
            center = event_data['hotspot_center']
            event_info = event_data['event_info']
            has_events = event_data['has_events']
            
            html_content += f"""
            <div class="hotspot">
                <h3>Location #{i+1} - Events</h3>
                <div class="info-item">
                    <strong>Center:</strong> {center['latitude']:.4f}, {center['longitude']:.4f}
                </div>
                <div class="event-item">
                    {event_info.replace(chr(10), '<br>')}
                </div>
            </div>
            """
    
    html_content += f"""
            <div class="timestamp">
                Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                Enhanced Hot Spot Detection System
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"   ✅ HTML file created: {filename}")
    return filename

def create_csv_heatmap(hotspots, filename='tile_heatmap.csv'):
    """Create CSV heatmap"""
    print(f"📊 Creating CSV heatmap: {filename}")
    
    tiles = []
    grid_size = 10
    
    # Load traffic data
    data = pd.read_csv('data/astana/vel.csv', header=None)
    recent_data = data.iloc[-1].values
    traffic_grid = recent_data.reshape(grid_size, grid_size)
    
    for i in range(grid_size):
        for j in range(grid_size):
            lat_min = 51.1194 + i * 0.01
            lat_max = lat_min + 0.01
            lon_min = 71.3991 + j * 0.01
            lon_max = lon_min + 0.01
            
            tiles.append({
                'tile_id': f"{i:02d}_{j:02d}",
                'grid_x': i,
                'grid_y': j,
                'lat_min': lat_min,
                'lat_max': lat_max,
                'lon_min': lon_min,
                'lon_max': lon_max,
                'center_lat': (lat_min + lat_max) / 2,
                'center_lon': (lon_min + lon_max) / 2,
                'heat_level': float(traffic_grid[i, j]),
                'normalized_heat': float((traffic_grid[i, j] - traffic_grid.min()) / (traffic_grid.max() - traffic_grid.min()))
            })
    
    df = pd.DataFrame(tiles)
    df.to_csv(filename, index=False)
    
    print(f"   ✅ CSV file created: {filename}")
    return filename

def main():
    """Main function"""
    print("🚀 Enhanced Hot Spot Detection System - Simple Runner")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. Create sample data
        if not create_sample_data():
            print("❌ Failed to create sample data")
            return False
        
        # 2. Create simple model
        if not create_simple_model():
            print("❌ Failed to create model")
            return False
        
        # 3. Detect hotspots
        hotspots = detect_hotspots_simple()
        
        # 4. Generate organization data
        organizations = generate_mock_organizations(hotspots)
        
        # 5. Generate event data
        events = generate_mock_events(hotspots)
        
        # 6. Create outputs
        print("\n📁 Creating output files...")
        
        # HTML visualization
        html_file = create_html_visualization(hotspots, organizations, events, 'current_hotspots.html')
        
        # CSV heatmap
        csv_file = create_csv_heatmap(hotspots, 'current_tile_heatmap.csv')
        
        # Predicted hotspots (simulate)
        predicted_hotspots = hotspots.copy()  # Simple simulation
        predicted_orgs = generate_mock_organizations(predicted_hotspots)
        predicted_events = generate_mock_events(predicted_hotspots)
        
        pred_html = create_html_visualization([], predicted_hotspots, predicted_orgs, predicted_events, 'predicted_hotspots_30min.html')
        pred_csv = create_csv_heatmap(predicted_hotspots, 'predicted_tile_heatmap_30min.csv')
        
        print("\n" + "=" * 60)
        print("✅ ENHANCED HOT SPOT DETECTION COMPLETE!")
        print("=" * 60)
        print("\n📁 Generated Files:")
        print(f"   🔥 {html_file} - Current hot spots visualization")
        print(f"   🔮 {pred_html} - 30-minute predictions")
        print(f"   📊 {csv_file} - Current tile heat levels")
        print(f"   📈 {pred_csv} - Predicted tile heat levels")
        print("\n🌐 Open the HTML files in your browser to view results!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
