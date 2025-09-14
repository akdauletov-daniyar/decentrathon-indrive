#!/usr/bin/env python3
"""
Enhanced Hot Spot Detection System with 2GIS API Integration
Combines STGCN predictions with real-world organization and event data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import existing STGCN modules
from model import models
from script import dataloader, utility
from sklearn.preprocessing import StandardScaler

class HotSpotDetector:
    """Enhanced hot spot detection with 2GIS API integration"""
    
    def __init__(self, dataset_name='astana', grid_size=10):
        self.dataset_name = dataset_name
        self.grid_size = grid_size
        self.n_sensors = grid_size * grid_size
        self.model = None
        self.scaler = None
        self.gso = None
        
        # API configurations (to be set by user)
        self.twogis_api_key = None
        self.openai_api_key = None
        
        # Hot spot detection parameters
        self.hotspot_threshold = 0.7  # Threshold for considering a location as hot spot
        self.tile_size_meters = 100  # 100m x 100m tiles
        
    def load_trained_model(self):
        """Load the trained STGCN model"""
        print(f"Loading trained model for {self.dataset_name}...")
        
        # Load adjacency matrix
        adj, n_vertex = dataloader.load_adj(self.dataset_name)
        gso = utility.calc_gso(adj, 'sym_norm_lap')
        gso = utility.calc_chebynet_gso(gso)
        gso = gso.toarray().astype(np.float32)
        self.gso = torch.from_numpy(gso)
        
        # Create model configuration
        class Args:
            def __init__(self):
                self.Kt = 3
                self.Ks = 3
                self.act_func = 'glu'
                self.graph_conv_type = 'cheb_graph_conv'
                self.gso = self.gso
                self.enable_bias = True
                self.droprate = 0.5
                self.n_his = 12
                self.n_pred = 3
        
        args = Args()
        blocks = [[1], [64, 16, 64], [64, 16, 64], [128, 128], [1]]
        
        # Create and load model
        if self.dataset_name == 'astana':
            self.model = models.STGCNChebGraphConv(args, blocks, n_vertex)
        else:
            self.model = models.STGCNGraphConv(args, blocks, n_vertex)
        
        # Load trained weights
        model_path = f"STGCN_{self.dataset_name}.pt"
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            print(f"✅ Model loaded from {model_path}")
        else:
            print(f"❌ Model file {model_path} not found!")
            return False
        
        self.model.eval()
        return True
    
    def prepare_prediction_data(self, n_his=12):
        """Prepare the latest data for prediction"""
        print("Preparing prediction data...")
        
        # Load velocity data
        data_path = f'data/{self.dataset_name}/vel.csv'
        if not os.path.exists(data_path):
            print(f"❌ Data file {data_path} not found!")
            return None
        
        data = pd.read_csv(data_path, header=None)
        print(f"Loaded data shape: {data.shape}")
        
        # Get the last n_his timesteps for prediction
        recent_data = data.iloc[-n_his:].values
        
        # Normalize the data
        self.scaler = StandardScaler()
        recent_data_scaled = self.scaler.fit_transform(recent_data)
        
        # Reshape for model input: [1, 1, n_his, n_vertex]
        input_data = torch.FloatTensor(recent_data_scaled).unsqueeze(0).unsqueeze(0)
        
        return input_data, recent_data
    
    def detect_current_hotspots(self, traffic_data):
        """Detect current hot spots from traffic data"""
        print("Detecting current hot spots...")
        
        # Reshape data to grid format
        if len(traffic_data.shape) == 1:
            traffic_grid = traffic_data.reshape(self.grid_size, self.grid_size)
        else:
            traffic_grid = traffic_data[-1].reshape(self.grid_size, self.grid_size)
        
        # Normalize traffic data for hot spot detection
        normalized_traffic = (traffic_grid - traffic_grid.min()) / (traffic_grid.max() - traffic_grid.min())
        
        # Find hot spots (areas with high traffic density)
        hotspots = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if normalized_traffic[i, j] > self.hotspot_threshold:
                    # Calculate center coordinates (assuming grid covers a specific area)
                    # For Astana, we'll use approximate coordinates
                    lat = 51.1694 + (i - self.grid_size/2) * 0.01  # Approximate latitude
                    lon = 71.4491 + (j - self.grid_size/2) * 0.01  # Approximate longitude
                    
                    hotspots.append({
                        'grid_x': i,
                        'grid_y': j,
                        'latitude': lat,
                        'longitude': lon,
                        'intensity': normalized_traffic[i, j],
                        'traffic_level': traffic_grid[i, j]
                    })
        
        print(f"Found {len(hotspots)} current hot spots")
        return hotspots
    
    def calculate_hotspot_centers(self, hotspots):
        """Calculate the center of each hot spot cluster"""
        print("Calculating hot spot centers...")
        
        if not hotspots:
            return []
        
        # Group nearby hot spots into clusters
        clusters = []
        used_hotspots = set()
        
        for i, hotspot in enumerate(hotspots):
            if i in used_hotspots:
                continue
            
            cluster = [hotspot]
            used_hotspots.add(i)
            
            # Find nearby hot spots
            for j, other_hotspot in enumerate(hotspots):
                if j in used_hotspots:
                    continue
                
                # Calculate distance between hot spots
                distance = np.sqrt((hotspot['grid_x'] - other_hotspot['grid_x'])**2 + 
                                 (hotspot['grid_y'] - other_hotspot['grid_y'])**2)
                
                if distance <= 2:  # Within 2 grid cells
                    cluster.append(other_hotspot)
                    used_hotspots.add(j)
            
            # Calculate cluster center
            if cluster:
                center_lat = np.mean([h['latitude'] for h in cluster])
                center_lon = np.mean([h['longitude'] for h in cluster])
                center_x = np.mean([h['grid_x'] for h in cluster])
                center_y = np.mean([h['grid_y'] for h in cluster])
                max_intensity = max([h['intensity'] for h in cluster])
                avg_traffic = np.mean([h['traffic_level'] for h in cluster])
                
                clusters.append({
                    'center_latitude': center_lat,
                    'center_longitude': center_lon,
                    'center_x': center_x,
                    'center_y': center_y,
                    'intensity': max_intensity,
                    'traffic_level': avg_traffic,
                    'hotspot_count': len(cluster),
                    'hotspots': cluster
                })
        
        print(f"Created {len(clusters)} hot spot clusters")
        return clusters
    
    def query_2gis_organizations(self, hotspot_centers):
        """Query 2GIS API for organizations near hot spot centers"""
        print("Querying 2GIS API for organization data...")
        
        if not self.twogis_api_key:
            print("⚠️ 2GIS API key not set. Using mock data.")
            return self._generate_mock_organization_data(hotspot_centers)
        
        organizations = []
        
        for center in hotspot_centers:
            try:
                # 2GIS API endpoint for nearby organizations
                url = "https://catalog.api.2gis.com/3.0/items"
                params = {
                    'key': self.twogis_api_key,
                    'point': f"{center['center_longitude']},{center['center_latitude']}",
                    'radius': 500,  # 500 meters radius
                    'type': 'branch',
                    'fields': 'items.point,items.name,items.type,items.schedule,items.rubrics',
                    'limit': 20  # Limit results
                }
                
                print(f"   🔍 Querying 2GIS for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}")
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    orgs = data.get('result', {}).get('items', [])
                    
                    print(f"   ✅ Found {len(orgs)} organizations")
                    
                    center_orgs = []
                    for org in orgs:
                        org_data = {
                            'name': org.get('name', 'Unknown'),
                            'type': org.get('type', 'Unknown'),
                            'latitude': org.get('point', {}).get('lat', center['center_latitude']),
                            'longitude': org.get('point', {}).get('lng', center['center_longitude']),
                            'schedule': org.get('schedule', {}),
                            'rubrics': org.get('rubrics', []),
                            'closing_time': self._extract_closing_time(org.get('schedule', {}))
                        }
                        center_orgs.append(org_data)
                    
                    organizations.append({
                        'hotspot_center': center,
                        'organizations': center_orgs,
                        'organization_count': len(center_orgs)
                    })
                    
                else:
                    print(f"   ⚠️ 2GIS API error (status {response.status_code}) for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}")
                    print(f"   📄 Response: {response.text[:200]}...")
                    organizations.append({
                        'hotspot_center': center,
                        'organizations': [],
                        'organization_count': 0
                    })
                    
            except requests.exceptions.Timeout:
                print(f"   ⚠️ 2GIS API timeout for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}")
                organizations.append({
                    'hotspot_center': center,
                    'organizations': [],
                    'organization_count': 0
                })
            except Exception as e:
                print(f"   ⚠️ Error querying 2GIS for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}: {e}")
                organizations.append({
                    'hotspot_center': center,
                    'organizations': [],
                    'organization_count': 0
                })
        
        return organizations
    
    def _generate_mock_organization_data(self, hotspot_centers):
        """Generate mock organization data for testing"""
        print("Generating mock organization data...")
        
        organization_types = [
            'restaurant', 'shopping_center', 'office_building', 'entertainment',
            'hotel', 'bank', 'pharmacy', 'gas_station', 'park', 'museum'
        ]
        
        organizations = []
        
        for center in hotspot_centers:
            # Generate 3-8 random organizations per hot spot
            n_orgs = np.random.randint(3, 9)
            center_orgs = []
            
            for _ in range(n_orgs):
                org_type = np.random.choice(organization_types)
                closing_hour = np.random.randint(18, 24)  # Random closing time between 6 PM and midnight
                
                org_data = {
                    'name': f"{org_type.replace('_', ' ').title()} {np.random.randint(1, 100)}",
                    'type': org_type,
                    'latitude': center['center_latitude'] + np.random.normal(0, 0.001),
                    'longitude': center['center_longitude'] + np.random.normal(0, 0.001),
                    'schedule': {'workdays': f'09:00-{closing_hour:02d}:00'},
                    'rubrics': [org_type],
                    'closing_time': closing_hour
                }
                center_orgs.append(org_data)
            
            organizations.append({
                'hotspot_center': center,
                'organizations': center_orgs,
                'organization_count': len(center_orgs)
            })
        
        return organizations
    
    def _extract_closing_time(self, schedule):
        """Extract closing time from 2GIS schedule data"""
        try:
            if 'workdays' in schedule:
                time_str = schedule['workdays']
                if '-' in time_str:
                    closing_time = time_str.split('-')[1]
                    hour = int(closing_time.split(':')[0])
                    return hour
        except:
            pass
        return 22  # Default closing time
    
    def query_events_with_chatgpt(self, hotspot_centers):
        """Query ChatGPT API for event information at hot spot locations"""
        print("Querying ChatGPT API for event information...")
        
        if not self.openai_api_key:
            print("⚠️ OpenAI API key not set. Using mock event data.")
            return self._generate_mock_event_data(hotspot_centers)
        
        events = []
        
        for center in hotspot_centers:
            try:
                # Prepare location information for ChatGPT
                location_info = f"Location: {center['center_latitude']:.4f}, {center['center_longitude']:.4f}"
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                prompt = f"""
                Search for ongoing events near coordinates {center['center_latitude']:.4f}, {center['center_longitude']:.4f} in Astana, Kazakhstan on {current_time}.
                Look for:
                1. Concerts, festivals, or cultural events
                2. Sports events or competitions
                3. Business conferences or meetings
                4. Public gatherings or demonstrations
                5. Special promotions or sales events
                
                Provide event details including name, type, time, and expected attendance if available.
                If no events found, respond with "No events found".
                """
                
                print(f"   🔍 Querying ChatGPT for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}")
                
                # ChatGPT API call
                headers = {
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 500,
                    'temperature': 0.7
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    event_info = result['choices'][0]['message']['content']
                    
                    print(f"   ✅ ChatGPT response received")
                    
                    events.append({
                        'hotspot_center': center,
                        'event_info': event_info,
                        'has_events': 'No events found' not in event_info.lower()
                    })
                else:
                    print(f"   ⚠️ ChatGPT API error (status {response.status_code}) for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}")
                    print(f"   📄 Response: {response.text[:200]}...")
                    events.append({
                        'hotspot_center': center,
                        'event_info': 'API error - no event data available',
                        'has_events': False
                    })
                    
            except requests.exceptions.Timeout:
                print(f"   ⚠️ ChatGPT API timeout for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}")
                events.append({
                    'hotspot_center': center,
                    'event_info': 'API timeout - no event data available',
                    'has_events': False
                })
            except Exception as e:
                print(f"   ⚠️ Error querying ChatGPT for center {center['center_latitude']:.4f}, {center['center_longitude']:.4f}: {e}")
                events.append({
                    'hotspot_center': center,
                    'event_info': f'Error: {str(e)}',
                    'has_events': False
                })
        
        return events
    
    def _generate_mock_event_data(self, hotspot_centers):
        """Generate mock event data for testing"""
        print("Generating mock event data...")
        
        event_types = [
            'concert', 'festival', 'sports_event', 'conference', 'exhibition',
            'street_fair', 'cultural_event', 'business_meeting', 'public_gathering'
        ]
        
        events = []
        
        for center in hotspot_centers:
            # 30% chance of having an event
            if np.random.random() < 0.3:
                event_type = np.random.choice(event_types)
                event_name = f"{event_type.replace('_', ' ').title()} at Location"
                attendance = np.random.randint(50, 2000)
                
                event_info = f"Event: {event_name}\nType: {event_type}\nExpected Attendance: {attendance} people\nTime: {datetime.now().strftime('%H:%M')}"
                has_events = True
            else:
                event_info = "No events found"
                has_events = False
            
            events.append({
                'hotspot_center': center,
                'event_info': event_info,
                'has_events': has_events
            })
        
        return events
    
    def refine_predictions_with_context(self, predictions, organizations, events):
        """Refine predictions using organization and event data"""
        print("Refining predictions with context data...")
        
        refined_predictions = predictions.copy()
        
        for i, (org_data, event_data) in enumerate(zip(organizations, events)):
            center = org_data['hotspot_center']
            grid_x, grid_y = int(center['center_x']), int(center['center_y'])
            
            # Calculate refinement factor based on context
            refinement_factor = 1.0
            
            # Organization-based refinement
            if org_data['organization_count'] > 0:
                # More organizations = higher activity
                org_factor = min(1.5, 1.0 + (org_data['organization_count'] / 10.0))
                refinement_factor *= org_factor
                
                # Check for late-closing organizations
                late_closing_orgs = sum(1 for org in org_data['organizations'] if org['closing_time'] > 20)
                if late_closing_orgs > 0:
                    refinement_factor *= 1.2
            
            # Event-based refinement
            if event_data['has_events']:
                # Events significantly increase activity
                refinement_factor *= 1.8
            
            # Apply refinement to predictions
            for t in range(len(refined_predictions)):
                if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                    sensor_idx = grid_y * self.grid_size + grid_x
                    if sensor_idx < len(refined_predictions[t]):
                        refined_predictions[t][sensor_idx] *= refinement_factor
        
        return refined_predictions
    
    def generate_tile_heatmap(self, predictions, timestep=0):
        """Generate tile-based heat map for specific timestep"""
        print(f"Generating tile heatmap for timestep {timestep}...")
        
        if timestep < len(predictions):
            traffic_data = predictions[timestep]
        else:
            traffic_data = predictions[-1]
        
        # Reshape to grid
        traffic_grid = traffic_data.reshape(self.grid_size, self.grid_size)
        
        # Create tile data
        tiles = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Calculate tile boundaries (approximate)
                lat_min = 51.1694 + (i - self.grid_size/2) * 0.01
                lat_max = lat_min + 0.01
                lon_min = 71.4491 + (j - self.grid_size/2) * 0.01
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
        
        return tiles
    
    def create_html_visualization(self, current_hotspots, predicted_hotspots, organizations, events, output_file='hotspot_visualization.html'):
        """Create HTML visualization of hot spots"""
        print(f"Creating HTML visualization: {output_file}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced Hot Spot Detection - Astana City</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.8;
                    font-size: 1.1em;
                }}
                .content {{
                    padding: 30px;
                }}
                .section {{
                    margin-bottom: 40px;
                    padding: 25px;
                    border-radius: 10px;
                    background: #f8f9fa;
                    border-left: 5px solid #3498db;
                }}
                .section h2 {{
                    margin-top: 0;
                    color: #2c3e50;
                    font-size: 1.8em;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 10px;
                }}
                .hotspot-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}
                .hotspot-card {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    border-left: 4px solid #e74c3c;
                    transition: transform 0.3s ease;
                }}
                .hotspot-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                }}
                .hotspot-card h3 {{
                    margin: 0 0 15px 0;
                    color: #e74c3c;
                    font-size: 1.3em;
                }}
                .hotspot-info {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-bottom: 15px;
                }}
                .info-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 12px;
                    background: #ecf0f1;
                    border-radius: 5px;
                    font-size: 0.9em;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #7f8c8d;
                }}
                .info-value {{
                    color: #2c3e50;
                }}
                .organizations {{
                    margin-top: 15px;
                }}
                .org-item {{
                    background: #e8f5e8;
                    padding: 8px 12px;
                    margin: 5px 0;
                    border-radius: 5px;
                    border-left: 3px solid #27ae60;
                    font-size: 0.9em;
                }}
                .events {{
                    margin-top: 15px;
                }}
                .event-item {{
                    background: #fff3cd;
                    padding: 8px 12px;
                    margin: 5px 0;
                    border-radius: 5px;
                    border-left: 3px solid #ffc107;
                    font-size: 0.9em;
                }}
                .no-data {{
                    text-align: center;
                    color: #7f8c8d;
                    font-style: italic;
                    padding: 20px;
                }}
                .timestamp {{
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ecf0f1;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔥 Enhanced Hot Spot Detection</h1>
                    <p>Real-time traffic analysis with organization and event data integration</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>📍 Current Hot Spots</h2>
                        <div class="hotspot-grid">
        """
        
        # Add current hot spots
        if current_hotspots:
            for i, hotspot in enumerate(current_hotspots):
                html_content += f"""
                            <div class="hotspot-card">
                                <h3>Hot Spot #{i+1}</h3>
                                <div class="hotspot-info">
                                    <div class="info-item">
                                        <span class="info-label">Coordinates:</span>
                                        <span class="info-value">{hotspot['latitude']:.4f}, {hotspot['longitude']:.4f}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Intensity:</span>
                                        <span class="info-value">{hotspot['intensity']:.2f}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Traffic Level:</span>
                                        <span class="info-value">{hotspot['traffic_level']:.1f} km/h</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Grid Position:</span>
                                        <span class="info-value">({hotspot['grid_x']}, {hotspot['grid_y']})</span>
                                    </div>
                                </div>
                            </div>
                """
        else:
            html_content += '<div class="no-data">No current hot spots detected</div>'
        
        html_content += """
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🔮 Predicted Hot Spots (30 minutes)</h2>
                        <div class="hotspot-grid">
        """
        
        # Add predicted hot spots
        if predicted_hotspots:
            for i, hotspot in enumerate(predicted_hotspots):
                html_content += f"""
                            <div class="hotspot-card">
                                <h3>Predicted Hot Spot #{i+1}</h3>
                                <div class="hotspot-info">
                                    <div class="info-item">
                                        <span class="info-label">Coordinates:</span>
                                        <span class="info-value">{hotspot['latitude']:.4f}, {hotspot['longitude']:.4f}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Intensity:</span>
                                        <span class="info-value">{hotspot['intensity']:.2f}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Traffic Level:</span>
                                        <span class="info-value">{hotspot['traffic_level']:.1f} km/h</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Grid Position:</span>
                                        <span class="info-value">({hotspot['grid_x']}, {hotspot['grid_y']})</span>
                                    </div>
                                </div>
                            </div>
                """
        else:
            html_content += '<div class="no-data">No predicted hot spots</div>'
        
        html_content += """
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🏢 Nearby Organizations</h2>
                        <div class="hotspot-grid">
        """
        
        # Add organization data
        if organizations:
            for i, org_data in enumerate(organizations):
                center = org_data['hotspot_center']
                orgs = org_data['organizations']
                
                html_content += f"""
                            <div class="hotspot-card">
                                <h3>Location #{i+1} - {org_data['organization_count']} Organizations</h3>
                                <div class="hotspot-info">
                                    <div class="info-item">
                                        <span class="info-label">Center:</span>
                                        <span class="info-value">{center['center_latitude']:.4f}, {center['center_longitude']:.4f}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Organizations:</span>
                                        <span class="info-value">{org_data['organization_count']}</span>
                                    </div>
                                </div>
                                <div class="organizations">
                """
                
                for org in orgs[:5]:  # Show first 5 organizations
                    html_content += f"""
                                    <div class="org-item">
                                        <strong>{org['name']}</strong><br>
                                        Type: {org['type']} | Closing: {org['closing_time']}:00
                                    </div>
                    """
                
                if len(orgs) > 5:
                    html_content += f'<div class="org-item">... and {len(orgs) - 5} more organizations</div>'
                
                html_content += """
                                </div>
                            </div>
                """
        else:
            html_content += '<div class="no-data">No organization data available</div>'
        
        html_content += """
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🎉 Event Information</h2>
                        <div class="hotspot-grid">
        """
        
        # Add event data
        if events:
            for i, event_data in enumerate(events):
                center = event_data['hotspot_center']
                event_info = event_data['event_info']
                has_events = event_data['has_events']
                
                html_content += f"""
                            <div class="hotspot-card">
                                <h3>Location #{i+1} - Events</h3>
                                <div class="hotspot-info">
                                    <div class="info-item">
                                        <span class="info-label">Center:</span>
                                        <span class="info-value">{center['center_latitude']:.4f}, {center['center_longitude']:.4f}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="info-label">Has Events:</span>
                                        <span class="info-value">{'Yes' if has_events else 'No'}</span>
                                    </div>
                                </div>
                                <div class="events">
                                    <div class="event-item">
                                        {event_info.replace(chr(10), '<br>')}
                                    </div>
                                </div>
                            </div>
                """
        else:
            html_content += '<div class="no-data">No event data available</div>'
        
        html_content += f"""
                        </div>
                    </div>
                    
                    <div class="timestamp">
                        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                        Enhanced Hot Spot Detection System v1.0
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML visualization saved to {output_file}")
        return output_file
    
    def save_tile_csv(self, tiles, output_file='tile_heatmap.csv'):
        """Save tile-based heat map to CSV"""
        print(f"Saving tile heatmap to {output_file}...")
        
        df = pd.DataFrame(tiles)
        df.to_csv(output_file, index=False)
        
        print(f"✅ Tile heatmap saved to {output_file}")
        return output_file
    
    def set_api_keys(self, twogis_key=None, openai_key=None):
        """Set API keys for external services"""
        self.twogis_api_key = twogis_key
        self.openai_api_key = openai_key
        
        if twogis_key:
            print("✅ 2GIS API key set")
        if openai_key:
            print("✅ OpenAI API key set")
    
    def run_enhanced_detection(self):
        """Run the complete enhanced hot spot detection pipeline"""
        print("🚀 Starting Enhanced Hot Spot Detection Pipeline")
        print("=" * 60)
        
        try:
            # 1. Load model and prepare data
            if not self.load_trained_model():
                return False
            
            input_data, recent_data = self.prepare_prediction_data()
            if input_data is None:
                return False
            
            # 2. Generate predictions
            print("\n📊 Generating traffic predictions...")
            predictions = []
            current_input = input_data.clone()
            
            with torch.no_grad():
                for step in range(12):  # 12 steps = 60 minutes
                    pred = self.model(current_input)
                    pred_reshaped = pred.view(1, 1, 1, self.n_sensors)
                    predictions.append(pred_reshaped.squeeze().numpy())
                    
                    # Update input for next prediction
                    current_input = torch.cat([
                        current_input[:, :, 1:, :],
                        pred_reshaped
                    ], dim=2)
            
            predictions = np.array(predictions)
            print(f"✅ Generated {len(predictions)} prediction steps")
            
            # 3. Detect current hot spots
            print("\n🔥 Detecting current hot spots...")
            current_hotspots = self.detect_current_hotspots(recent_data)
            
            # 4. Calculate hot spot centers
            print("\n📍 Calculating hot spot centers...")
            current_centers = self.calculate_hotspot_centers(current_hotspots)
            
            # 5. Query external APIs
            print("\n🌐 Querying external APIs...")
            organizations = self.query_2gis_organizations(current_centers)
            events = self.query_events_with_chatgpt(current_centers)
            
            # 6. Refine predictions with context
            print("\n🎯 Refining predictions with context data...")
            refined_predictions = self.refine_predictions_with_context(predictions, organizations, events)
            
            # 7. Detect predicted hot spots
            print("\n🔮 Detecting predicted hot spots...")
            predicted_hotspots = self.detect_current_hotspots(refined_predictions[5])  # 30 minutes ahead
            
            # 8. Generate outputs
            print("\n📁 Generating output files...")
            
            # Current hot spots HTML
            self.create_html_visualization(
                current_hotspots, 
                predicted_hotspots, 
                organizations, 
                events, 
                'current_hotspots.html'
            )
            
            # Predicted hot spots HTML (30 minutes)
            predicted_centers = self.calculate_hotspot_centers(predicted_hotspots)
            predicted_orgs = self.query_2gis_organizations(predicted_centers)
            predicted_events = self.query_events_with_chatgpt(predicted_centers)
            
            self.create_html_visualization(
                [], 
                predicted_hotspots, 
                predicted_orgs, 
                predicted_events, 
                'predicted_hotspots_30min.html'
            )
            
            # Current tile CSV
            current_tiles = self.generate_tile_heatmap(refined_predictions[0])
            self.save_tile_csv(current_tiles, 'current_tile_heatmap.csv')
            
            # Predicted tile CSV (30 minutes)
            predicted_tiles = self.generate_tile_heatmap(refined_predictions[5])
            self.save_tile_csv(predicted_tiles, 'predicted_tile_heatmap_30min.csv')
            
            print("\n" + "=" * 60)
            print("✅ ENHANCED HOT SPOT DETECTION COMPLETE!")
            print("=" * 60)
            print("\n📁 Generated Files:")
            print("   🔥 current_hotspots.html - Current hot spots visualization")
            print("   🔮 predicted_hotspots_30min.html - 30-minute predictions")
            print("   📊 current_tile_heatmap.csv - Current tile heat levels")
            print("   📈 predicted_tile_heatmap_30min.csv - Predicted tile heat levels")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in enhanced detection pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    print("🚀 Enhanced Hot Spot Detection System")
    print("=" * 50)
    
    # Initialize detector
    detector = HotSpotDetector(dataset_name='astana', grid_size=10)
    
    # Set API keys (replace with actual keys)
    # detector.set_api_keys(
    #     twogis_key="your_2gis_api_key_here",
    #     openai_key="your_openai_api_key_here"
    # )
    
    # Run detection
    success = detector.run_enhanced_detection()
    
    if success:
        print("\n🎯 Enhanced hot spot detection completed successfully!")
        print("📁 Check the generated HTML and CSV files for results.")
    else:
        print("\n❌ Enhanced hot spot detection failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
