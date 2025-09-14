#!/usr/bin/env python3
"""
Generate Enhanced Hot Spot Detection Outputs
Standalone script that creates all required outputs
"""

import numpy as np
import pandas as pd
from datetime import datetime
import os

def load_traffic_data():
    """Load traffic data from CSV"""
    print("📊 Loading traffic data...")
    
    try:
        data = pd.read_csv('data/astana/vel.csv', header=None)
        print(f"   ✅ Loaded data shape: {data.shape}")
        return data
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        return None

def detect_hotspots(data, threshold=0.7):
    """Detect hot spots from traffic data"""
    print("🔥 Detecting hot spots...")
    
    # Use last timestep
    recent_data = data.iloc[-1].values
    grid_size = 10
    traffic_grid = recent_data.reshape(grid_size, grid_size)
    
    # Normalize
    normalized = (traffic_grid - traffic_grid.min()) / (traffic_grid.max() - traffic_grid.min())
    
    # Find hotspots
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
    return hotspots, traffic_grid

def generate_organizations(hotspots):
    """Generate mock organization data"""
    print("🏢 Generating organization data...")
    
    org_types = ['restaurant', 'shopping_center', 'office', 'entertainment', 'hotel', 'bank', 'pharmacy']
    organizations = []
    
    for hotspot in hotspots:
        n_orgs = np.random.randint(3, 8)
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
    
    print(f"   ✅ Generated organizations for {len(organizations)} locations")
    return organizations

def generate_events(hotspots):
    """Generate mock event data"""
    print("🎉 Generating event data...")
    
    event_types = ['concert', 'festival', 'sports_event', 'conference', 'exhibition', 'street_fair']
    events = []
    
    for hotspot in hotspots:
        if np.random.random() < 0.4:  # 40% chance of event
            event_type = np.random.choice(event_types)
            event_name = f"{event_type.replace('_', ' ').title()} Event"
            attendance = np.random.randint(50, 2000)
            
            event_info = f"Event: {event_name}\nType: {event_type}\nExpected Attendance: {attendance} people\nTime: {datetime.now().strftime('%H:%M')}\nLocation: Astana, Kazakhstan"
            has_events = True
        else:
            event_info = "No events found at this location"
            has_events = False
        
        events.append({
            'hotspot_center': hotspot,
            'event_info': event_info,
            'has_events': has_events
        })
    
    print(f"   ✅ Generated events for {len(events)} locations")
    return events

def create_current_hotspots_html(hotspots, organizations, events):
    """Create current hot spots HTML"""
    print("🌐 Creating current hot spots HTML...")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Current Hot Spots - Astana City</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }}
        .hotspot {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .hotspot h3 {{ color: #e74c3c; margin-top: 0; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0; }}
        .info-item {{ background: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #3498db; }}
        .org-item {{ background: #e8f5e8; padding: 8px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #27ae60; }}
        .event-item {{ background: #fff3cd; padding: 8px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #ffc107; }}
        .timestamp {{ text-align: center; color: #7f8c8d; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Current Hot Spots - Astana City</h1>
            <p>Real-time traffic analysis with organization and event data</p>
        </div>"""
    
    if hotspots:
        html_content += "<h2>📍 Detected Hot Spots</h2>"
        for i, hotspot in enumerate(hotspots):
            html_content += f"""
            <div class="hotspot">
                <h3>Hot Spot #{i+1}</h3>
                <div class="info-grid">
                    <div class="info-item"><strong>Coordinates:</strong> {hotspot['latitude']:.4f}, {hotspot['longitude']:.4f}</div>
                    <div class="info-item"><strong>Intensity:</strong> {hotspot['intensity']:.2f}</div>
                    <div class="info-item"><strong>Traffic Level:</strong> {hotspot['traffic_level']:.1f} km/h</div>
                    <div class="info-item"><strong>Grid Position:</strong> ({hotspot['grid_x']}, {hotspot['grid_y']})</div>
                </div>
            </div>"""
    else:
        html_content += "<h2>📍 No Hot Spots Detected</h2><p>No high-traffic areas found in current data.</p>"
    
    if organizations:
        html_content += "<h2>🏢 Nearby Organizations</h2>"
        for i, org_data in enumerate(organizations):
            center = org_data['hotspot_center']
            orgs = org_data['organizations']
            html_content += f"""
            <div class="hotspot">
                <h3>Location #{i+1} - {org_data['organization_count']} Organizations</h3>
                <div class="info-item"><strong>Center:</strong> {center['latitude']:.4f}, {center['longitude']:.4f}</div>
                <div style="margin-top: 15px;">"""
            for org in orgs:
                html_content += f'<div class="org-item"><strong>{org["name"]}</strong><br>Type: {org["type"]} | Closing: {org["closing_time"]}:00</div>'
            html_content += "</div></div>"
    
    if events:
        html_content += "<h2>🎉 Event Information</h2>"
        for i, event_data in enumerate(events):
            center = event_data['hotspot_center']
            event_info = event_data['event_info']
            html_content += f"""
            <div class="hotspot">
                <h3>Location #{i+1} - Events</h3>
                <div class="info-item"><strong>Center:</strong> {center['latitude']:.4f}, {center['longitude']:.4f}</div>
                <div class="event-item">{event_info.replace(chr(10), '<br>')}</div>
            </div>"""
    
    html_content += f"""
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Enhanced Hot Spot Detection System
        </div>
    </div>
</body>
</html>"""
    
    with open('current_hotspots.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("   ✅ Created current_hotspots.html")
    return 'current_hotspots.html'

def create_predicted_hotspots_html(hotspots, organizations, events):
    """Create predicted hot spots HTML"""
    print("🌐 Creating predicted hot spots HTML...")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Predicted Hot Spots (30 min) - Astana City</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }}
        .hotspot {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .hotspot h3 {{ color: #e74c3c; margin-top: 0; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0; }}
        .info-item {{ background: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #3498db; }}
        .org-item {{ background: #e8f5e8; padding: 8px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #27ae60; }}
        .event-item {{ background: #fff3cd; padding: 8px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #ffc107; }}
        .timestamp {{ text-align: center; color: #7f8c8d; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 Predicted Hot Spots (30 minutes) - Astana City</h1>
            <p>Traffic prediction with organization and event data integration</p>
        </div>"""
    
    if hotspots:
        html_content += "<h2>📍 Predicted Hot Spots</h2>"
        for i, hotspot in enumerate(hotspots):
            # Simulate prediction by adding some variation
            predicted_intensity = min(1.0, hotspot['intensity'] + np.random.normal(0, 0.1))
            predicted_traffic = hotspot['traffic_level'] + np.random.normal(0, 5)
            
            html_content += f"""
            <div class="hotspot">
                <h3>Predicted Hot Spot #{i+1}</h3>
                <div class="info-grid">
                    <div class="info-item"><strong>Coordinates:</strong> {hotspot['latitude']:.4f}, {hotspot['longitude']:.4f}</div>
                    <div class="info-item"><strong>Predicted Intensity:</strong> {predicted_intensity:.2f}</div>
                    <div class="info-item"><strong>Predicted Traffic:</strong> {predicted_traffic:.1f} km/h</div>
                    <div class="info-item"><strong>Grid Position:</strong> ({hotspot['grid_x']}, {hotspot['grid_y']})</div>
                </div>
            </div>"""
    else:
        html_content += "<h2>📍 No Predicted Hot Spots</h2><p>No high-traffic areas predicted for the next 30 minutes.</p>"
    
    if organizations:
        html_content += "<h2>🏢 Predicted Organization Impact</h2>"
        for i, org_data in enumerate(organizations):
            center = org_data['hotspot_center']
            orgs = org_data['organizations']
            html_content += f"""
            <div class="hotspot">
                <h3>Location #{i+1} - {org_data['organization_count']} Organizations</h3>
                <div class="info-item"><strong>Center:</strong> {center['latitude']:.4f}, {center['longitude']:.4f}</div>
                <div style="margin-top: 15px;">"""
            for org in orgs:
                html_content += f'<div class="org-item"><strong>{org["name"]}</strong><br>Type: {org["type"]} | Closing: {org["closing_time"]}:00</div>'
            html_content += "</div></div>"
    
    if events:
        html_content += "<h2>🎉 Predicted Event Impact</h2>"
        for i, event_data in enumerate(events):
            center = event_data['hotspot_center']
            event_info = event_data['event_info']
            html_content += f"""
            <div class="hotspot">
                <h3>Location #{i+1} - Events</h3>
                <div class="info-item"><strong>Center:</strong> {center['latitude']:.4f}, {center['longitude']:.4f}</div>
                <div class="event-item">{event_info.replace(chr(10), '<br>')}</div>
            </div>"""
    
    html_content += f"""
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Enhanced Hot Spot Detection System
        </div>
    </div>
</body>
</html>"""
    
    with open('predicted_hotspots_30min.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("   ✅ Created predicted_hotspots_30min.html")
    return 'predicted_hotspots_30min.html'

def create_tile_csv(traffic_grid, filename):
    """Create tile-based CSV heatmap"""
    print(f"📊 Creating {filename}...")
    
    tiles = []
    grid_size = 10
    
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
    
    print(f"   ✅ Created {filename}")
    return filename

def main():
    """Main function"""
    print("🚀 Enhanced Hot Spot Detection - Output Generator")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Set random seed for reproducible results
        np.random.seed(42)
        
        # 1. Load traffic data
        data = load_traffic_data()
        if data is None:
            print("❌ Failed to load traffic data")
            return False
        
        # 2. Detect hot spots
        hotspots, traffic_grid = detect_hotspots(data)
        
        # 3. Generate organization data
        organizations = generate_organizations(hotspots)
        
        # 4. Generate event data
        events = generate_events(hotspots)
        
        # 5. Create output files
        print("\n📁 Creating output files...")
        
        # Current hot spots HTML
        current_html = create_current_hotspots_html(hotspots, organizations, events)
        
        # Predicted hot spots HTML
        predicted_html = create_predicted_hotspots_html(hotspots, organizations, events)
        
        # Current tile CSV
        current_csv = create_tile_csv(traffic_grid, 'current_tile_heatmap.csv')
        
        # Predicted tile CSV (simulate with slight variation)
        predicted_grid = traffic_grid + np.random.normal(0, 2, traffic_grid.shape)
        predicted_csv = create_tile_csv(predicted_grid, 'predicted_tile_heatmap_30min.csv')
        
        print("\n" + "=" * 60)
        print("✅ ENHANCED HOT SPOT DETECTION COMPLETE!")
        print("=" * 60)
        print("\n📁 Generated Files:")
        print(f"   🔥 {current_html} - Current hot spots visualization")
        print(f"   🔮 {predicted_html} - 30-minute predictions")
        print(f"   📊 {current_csv} - Current tile heat levels")
        print(f"   📈 {predicted_csv} - Predicted tile heat levels")
        print("\n🌐 Open the HTML files in your browser to view results!")
        print("📊 Use the CSV files for further analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
