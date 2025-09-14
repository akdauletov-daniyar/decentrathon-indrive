# 🔥 Enhanced Hot Spot Detection System

A powerful traffic prediction system that combines Spatio-Temporal Graph Convolutional Networks (STGCN) with real-world organization and event data to provide accurate hot spot detection and prediction for urban areas.

## 🌟 Features

- **🚗 STGCN Traffic Prediction**: Advanced neural network-based traffic forecasting
- **🏢 2GIS API Integration**: Real-time organization and business data
- **🎉 ChatGPT Event Detection**: Live event information and crowd predictions
- **📍 Hot Spot Detection**: Intelligent identification of high-traffic areas
- **🔮 Predictive Analytics**: 30-minute traffic predictions with context
- **📊 Interactive Visualizations**: Beautiful HTML dashboards
- **📈 Data Export**: CSV files with tile-based heat levels
- **🌐 Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Option 1: View Generated Outputs (Immediate)

The system has already generated output files that you can view immediately:

1. **Open HTML files** in your web browser:
   - `current_hotspots.html` - Current hot spots visualization
   - `predicted_hotspots_30min.html` - 30-minute predictions

2. **View CSV data** in Excel or any spreadsheet application:
   - `current_tile_heatmap.csv` - Current tile heat levels
   - `predicted_tile_heatmap_30min.csv` - Predicted tile heat levels

### Option 2: Run the Full System

1. **Install Python** (3.7 or higher)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the system**:
   ```bash
   python run_enhanced_detection.py
   ```

## 💻 Installation

### Prerequisites

- **Python 3.7+** (Download from [python.org](https://python.org))
- **Internet connection** (for API calls)
- **Web browser** (for viewing visualizations)

### Step 1: Download and Setup

1. **Download** this repository to your computer
2. **Open terminal/command prompt** in the project directory
3. **Verify Python installation**:
   ```bash
   python --version
   ```

### Step 2: Install Dependencies

Choose the installation option that fits your needs:

#### Option A: Minimal Installation (Recommended for basic use)
```bash
# Install only essential dependencies
pip install -r requirements-minimal.txt
```

#### Option B: Full Installation (Recommended for advanced features)
```bash
# Install all dependencies including optional features
pip install -r requirements.txt
```

#### Option C: Development Installation (For contributors)
```bash
# Install all dependencies including development tools
pip install -r requirements-dev.txt
```

#### Option D: Manual Installation
```bash
# Install core dependencies individually
pip install numpy pandas torch scikit-learn matplotlib requests python-dotenv
```

### Step 3: Verify Installation

```bash
# Test the installation
python test_enhanced_system.py
```

## ⚙️ Configuration

### API Keys Setup (Optional but Recommended)

The system works without API keys using mock data, but for real-world data:

1. **Get API Keys**:
   - **2GIS API**: [2gis.ru/api](https://2gis.ru/api) (for organization data)
   - **OpenAI API**: [platform.openai.com](https://platform.openai.com/api-keys) (for event data)

2. **Configure API Keys**:
   ```bash
   python setup_api_keys.py
   ```
   
   Or manually edit `script/.env`:
   ```env
   DGIS_API_KEY=your_2gis_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Configuration Options

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

## 🎯 Usage

### Basic Usage

#### 1. **Quick Demo** (No API keys needed)
```bash
python demo_enhanced_system.py
```
This creates sample data and runs the system with mock data.

#### 2. **Full System** (With real APIs)
```bash
python run_enhanced_detection.py
```
This uses your configured API keys for real-world data.

#### 3. **Test APIs**
```bash
python test_api_connectivity.py
```
This verifies that your API keys are working correctly.

### Advanced Usage

#### 1. **Custom Dataset**
```python
from enhanced_hotspot_detection import HotSpotDetector

# Initialize with custom parameters
detector = HotSpotDetector(dataset_name='astana', grid_size=10)

# Set API keys
detector.set_api_keys(
    twogis_key="your_2gis_key",
    openai_key="your_openai_key"
)

# Run detection
detector.run_enhanced_detection()
```

#### 2. **Custom Configuration**
```python
# Modify detection parameters
detector.hotspot_threshold = 0.8  # Higher threshold
detector.tile_size_meters = 50    # Smaller tiles

# Run with custom settings
detector.run_enhanced_detection()
```

## 📁 Output Files

The system generates the following files:

### HTML Visualizations

#### `current_hotspots.html`
- **Interactive dashboard** of current hot spots
- **Organization listings** with business details
- **Event information** and schedules
- **Real-time statistics** and metrics

#### `predicted_hotspots_30min.html`
- **30-minute predictions** with confidence scores
- **Predicted organization impact**
- **Event-based traffic forecasts**
- **Trend analysis** and insights

### CSV Data Files

#### `current_tile_heatmap.csv`
```csv
tile_id,grid_x,grid_y,lat_min,lat_max,lon_min,lon_max,center_lat,center_lon,heat_level,normalized_heat
00_00,0,0,51.1194,51.1294,71.3991,71.4091,51.1244,71.4041,25.2,0.45
00_01,0,1,51.1194,51.1294,71.4091,71.4191,51.1244,71.4141,24.77,0.44
...
```

#### `predicted_tile_heatmap_30min.csv`
- Same format as current data
- Contains 30-minute predictions
- Includes confidence adjustments

### Data Structure

Each CSV file contains:
- **tile_id**: Unique identifier (e.g., "00_00")
- **grid_x, grid_y**: Grid coordinates
- **lat_min, lat_max**: Latitude boundaries
- **lon_min, lon_max**: Longitude boundaries
- **center_lat, center_lon**: Tile center coordinates
- **heat_level**: Traffic speed in km/h
- **normalized_heat**: Normalized value (0-1)

## 📦 Requirements Files

The project includes three different requirements files for different use cases:

### `requirements-minimal.txt` (Recommended for basic use)
Contains only the essential dependencies needed to run the system:
- Core data processing libraries (numpy, pandas, scikit-learn)
- Deep learning framework (torch)
- Basic visualization (matplotlib)
- API communication (requests)
- Environment management (python-dotenv)

### `requirements.txt` (Recommended for full features)
Includes all dependencies for complete functionality:
- All minimal requirements
- Advanced data processing (openpyxl)
- Enhanced HTTP support (urllib3)
- API validation (jsonschema)
- Optional visualizations (plotly, seaborn)
- Geographic data processing (geopandas, folium)
- Development tools (pytest, jupyter)

### `requirements-dev.txt` (For developers and contributors)
Includes everything plus development tools:
- All requirements from requirements.txt
- Code formatting and linting (black, flake8, mypy)
- Testing frameworks (pytest, pytest-cov)
- Documentation tools (sphinx)
- Performance monitoring (memory-profiler)
- API testing tools (httpx, responses)

### Installation Recommendations

- **New users**: Start with `requirements-minimal.txt`
- **Advanced users**: Use `requirements.txt` for full features
- **Developers**: Use `requirements-dev.txt` for development

## 🔧 Troubleshooting

### Common Issues

#### 1. **Python Not Found**
```bash
# Windows
python --version
# If not found, install Python from python.org

# macOS
python3 --version
# If not found: brew install python3

# Linux
python3 --version
# If not found: sudo apt install python3
```

#### 2. **Module Import Errors**
```bash
# Install missing packages
pip install numpy pandas torch scikit-learn matplotlib requests python-dotenv

# Or reinstall all requirements
pip install -r requirements.txt
```

#### 3. **API Connection Issues**
```bash
# Test API connectivity
python test_api_connectivity.py

# Check internet connection
ping google.com

# Verify API keys in script/.env
```

#### 4. **Permission Errors**
```bash
# Windows: Run as Administrator
# macOS/Linux: Use sudo if needed
sudo python run_enhanced_detection.py
```

#### 5. **Memory Issues**
```python
# Reduce grid size in config.py
GRID_SIZE = 5  # Instead of 10

# Reduce prediction steps
PREDICTION_STEPS = 6  # Instead of 12
```

### Error Messages and Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Install missing package with `pip install package_name` |
| `API timeout` | Check internet connection and API key validity |
| `File not found` | Ensure data files exist in `data/astana/` directory |
| `Permission denied` | Run with appropriate permissions or change file location |
| `Memory error` | Reduce grid size or prediction steps |

## 🖥️ System Requirements

### Minimum Requirements

- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.7 or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 1GB free space
- **Internet**: Required for API calls

### Recommended Requirements

- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 2GB free space
- **Internet**: Stable broadband connection

### Browser Compatibility

The HTML visualizations work with:
- **Chrome** 90+ (Recommended)
- **Firefox** 88+
- **Safari** 14+
- **Edge** 90+

## 📚 Examples

### Example 1: Basic Usage
```bash
# Run with default settings
python run_enhanced_detection.py

# View results
open current_hotspots.html
```

### Example 2: Custom Configuration
```python
from enhanced_hotspot_detection import HotSpotDetector

# Create detector with custom settings
detector = HotSpotDetector(grid_size=15, threshold=0.6)

# Set API keys
detector.set_api_keys("your_key", "your_key")

# Run detection
detector.run_enhanced_detection()
```

### Example 3: Data Analysis
```python
import pandas as pd

# Load tile data
df = pd.read_csv('current_tile_heatmap.csv')

# Find highest heat tiles
high_heat = df[df['normalized_heat'] > 0.8]

# Analyze patterns
print(f"High heat tiles: {len(high_heat)}")
print(f"Average heat: {df['heat_level'].mean():.2f} km/h")
```

## 🤝 Support

### Getting Help

1. **Check the troubleshooting section** above
2. **Review error messages** carefully
3. **Verify system requirements** are met
4. **Test with demo mode** first

### Common Questions

**Q: Do I need API keys to use the system?**
A: No, the system works with mock data. API keys provide real-world data.

**Q: Can I use this with other cities?**
A: Yes, modify the coordinates in `config.py` for your city.

**Q: How accurate are the predictions?**
A: Accuracy depends on data quality and API availability. Real APIs provide better results.

**Q: Can I run this on a server?**
A: Yes, the system works on any Python-compatible server.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🔥 Enhanced Hot Spot Detection System v1.0**  
*Combining AI with real-world data for smarter traffic prediction*

**Ready to use? Start with the [Quick Start](#-quick-start) section!**