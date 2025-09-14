# Enhanced Hot Spot Detection System

An advanced traffic prediction system that combines Spatio-Temporal Graph Convolutional Networks (STGCN) with real-world organization and event data to provide accurate hot spot detection and prediction.

## 🚀 Features

- **STGCN-based Traffic Prediction**: Uses trained neural networks to predict traffic patterns
- **2GIS API Integration**: Queries nearby organizations and businesses for context
- **Event Detection**: Uses ChatGPT API to find ongoing events at hot spot locations
- **Refined Predictions**: Combines traffic data with real-world context for better accuracy
- **Interactive Visualizations**: Beautiful HTML dashboards for current and predicted hot spots
- **Tile-based Analysis**: CSV exports with 100m x 100m tile heat levels

## 📋 Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

### API Keys (Optional)
- **2GIS API Key**: For organization data (get from https://2gis.ru/api)
- **OpenAI API Key**: For event information (get from https://platform.openai.com/api-keys)

*Note: The system works without API keys using mock data for testing*

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the STGCN Model (if not already done)
```bash
python main.py --dataset astana --epochs 100
```

### 3. Configure API Keys (Optional)
```bash
python setup_api_keys.py
```

## 🚀 Usage

### Quick Start
```bash
python run_enhanced_detection.py
```

### Manual Usage
```python
from enhanced_hotspot_detection import HotSpotDetector

# Initialize detector
detector = HotSpotDetector(dataset_name='astana', grid_size=10)

# Set API keys (optional)
detector.set_api_keys(
    twogis_key="your_2gis_api_key",
    openai_key="your_openai_api_key"
)

# Run detection
detector.run_enhanced_detection()
```

## 📁 Output Files

The system generates the following files:

### HTML Visualizations
- `current_hotspots.html` - Interactive visualization of current hot spots
- `predicted_hotspots_30min.html` - 30-minute prediction visualization

### CSV Data
- `current_tile_heatmap.csv` - Current tile-based heat levels
- `predicted_tile_heatmap_30min.csv` - Predicted tile heat levels (30 minutes)

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Hot spot detection threshold (0.0-1.0)
HOTSPOT_THRESHOLD = 0.7

# Tile size in meters
TILE_SIZE_METERS = 100

# Grid configuration
GRID_SIZE = 10  # 10x10 grid

# Prediction parameters
PREDICTION_STEPS = 12  # 12 * 5min = 60min
```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   STGCN Model   │───▶│  Hot Spot        │───▶│  2GIS API       │
│   (Traffic      │    │  Detection       │    │  (Organizations)│
│   Prediction)   │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Refined         │◀───│  ChatGPT API    │
                       │  Predictions     │    │  (Events)       │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  HTML/CSV        │
                       │  Outputs         │
                       └──────────────────┘
```

## 📊 Data Flow

1. **Traffic Data Input**: Load recent traffic data from CSV
2. **STGCN Prediction**: Generate traffic predictions using trained model
3. **Hot Spot Detection**: Identify areas with high traffic density
4. **Center Calculation**: Calculate centers of hot spot clusters
5. **API Queries**: Query 2GIS for organizations and ChatGPT for events
6. **Prediction Refinement**: Adjust predictions based on context data
7. **Output Generation**: Create HTML visualizations and CSV exports

## 🎯 Hot Spot Detection Algorithm

1. **Normalize Traffic Data**: Scale traffic values to 0-1 range
2. **Apply Threshold**: Identify cells above hotspot threshold (default: 0.7)
3. **Cluster Analysis**: Group nearby hot spots into clusters
4. **Center Calculation**: Calculate weighted centers of clusters
5. **Context Integration**: Enhance with organization and event data

## 📈 Prediction Refinement

The system refines predictions using:

- **Organization Density**: More organizations = higher activity
- **Closing Times**: Late-closing businesses increase evening activity
- **Event Presence**: Events significantly boost predicted activity
- **Spatial Correlation**: Nearby hot spots influence each other

## 🔍 API Integration Details

### 2GIS API
- **Endpoint**: `https://catalog.api.2gis.com/3.0/items`
- **Purpose**: Query nearby organizations and businesses
- **Data Retrieved**: Name, type, schedule, closing times, rubrics

### ChatGPT API
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Purpose**: Search for ongoing events at hot spot locations
- **Data Retrieved**: Event names, types, times, expected attendance

## 🛡️ Error Handling

The system includes robust error handling:

- **API Failures**: Falls back to mock data if APIs are unavailable
- **Model Errors**: Graceful degradation with informative error messages
- **Data Validation**: Checks for required files and valid data formats
- **Network Timeouts**: Configurable timeout settings for API calls

## 📝 Example Output

### HTML Visualization
- Interactive hot spot maps
- Organization listings with details
- Event information and schedules
- Real-time statistics and metrics

### CSV Data Format
```csv
tile_id,grid_x,grid_y,lat_min,lat_max,lon_min,lon_max,center_lat,center_lon,heat_level,normalized_heat
00_00,0,0,51.1194,51.1294,71.3991,71.4091,51.1244,71.4041,25.2,0.45
00_01,0,1,51.1194,51.1294,71.4091,71.4191,51.1244,71.4141,28.7,0.52
...
```

## 🔧 Troubleshooting

### Common Issues

1. **Model Not Found**
   - Ensure `STGCN_astana.pt` exists
   - Run training: `python main.py --dataset astana`

2. **API Errors**
   - Check API keys in `config.py`
   - Verify internet connection
   - System will use mock data if APIs fail

3. **Missing Dependencies**
   - Run: `pip install -r requirements.txt`
   - Check Python version (3.7+)

4. **Data Files Missing**
   - Ensure `data/astana/` directory exists
   - Run dataset creation: `python create_astana_dataset.py`

## 📚 References

- [STGCN Paper](https://arxiv.org/abs/1709.04875)
- [2GIS API Documentation](https://docs.2gis.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify API keys are correct

---

**Enhanced Hot Spot Detection System v1.0**  
*Combining AI with real-world data for smarter traffic prediction*
