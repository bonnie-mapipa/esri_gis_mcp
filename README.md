# eThekwini ESRI GIS MCP

A Model Context Protocol (MCP) server for accessing eThekwini municipality's open GIS data portal.

## Overview

This MCP server provides seamless access to eThekwini municipality's geographic information system (GIS) data through their ArcGIS REST services. It automatically discovers available datasets and services from the eThekwini GIS portal, enabling easy querying and analysis of municipal spatial data.

**✅ Successfully connects to 141+ eThekwini datasets including:**
- Property leases and land information
- Roads and transportation infrastructure  
- Municipal boundaries and administrative areas
- Environmental data (wetlands, coastal zones, flood plains)
- Public facilities (schools, hospitals, libraries)
- Utilities and infrastructure data
- Planning and zoning information

## Features

### 🔄 **Auto-Discovery**
- Automatically discovers available datasets from eThekwini's open data portal
- Detects new datasets and services when they are added to the portal
- Intelligent caching with configurable refresh intervals

### 🔍 **Comprehensive Search**
- Search datasets by keywords, categories, and tags
- Filter by municipal service categories (Transportation, Environment, etc.)
- Full-text search across dataset names, descriptions, and metadata

### 🗺️ **Spatial Querying**
- Query feature layers with spatial and attribute filters
- Bounding box queries for geographic areas of interest
- Buffer queries around specific coordinates
- Support for various spatial relationships (intersects, contains, within, etc.)

### 📊 **Statistical Analysis**
- Get statistical information from numeric fields (count, sum, min, max, avg, stddev)
- Field information and metadata extraction
- Layer schema discovery

### 🛠️ **Municipal Services Integration**
- List available municipal service categories
- Categorized access to datasets by service type
- Municipal-specific data structures and workflows

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/bonnie-mapipa/ethekwini-gis-mcp.git
cd ethekwini-gis-mcp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the MCP server:**
```bash
python src/ethekwini_gis_mcp.py
```

## Configuration

### MCP Client Configuration

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "ethekwini-gis": {
      "command": "python",
      "args": ["src/ethekwini_gis_mcp.py"],
      "cwd": "/path/to/ethekwini-gis-mcp",
      "env": {}
    }
  }
}
```

### Environment Variables

Optional configuration through environment variables:

```bash
# Refresh interval in seconds (default: 900 = 15 minutes)
export ETHEKWINI_REFRESH_INTERVAL=900

# Maximum records per query (default: 100)
export ETHEKWINI_MAX_RECORDS=100

# HTTP timeout in seconds (default: 60)
export ETHEKWINI_TIMEOUT=60
```

## Available Tools

### Dataset Discovery
- **`refresh_datasets`** - Refresh and discover new datasets and services
- **`search_datasets`** - Search datasets by keywords, categories, or tags
- **`get_dataset_info`** - Get detailed information about a specific dataset
- **`list_municipal_services`** - List available municipal service categories

### Data Querying
- **`query_feature_layer`** - Query features from a dataset's feature layer
- **`spatial_query_by_coordinates`** - Query features within a bounding box or near coordinates
- **`get_layer_fields`** - Get field information for a feature layer
- **`get_layer_statistics`** - Get statistics for numeric fields in a layer

## Usage Examples

### Search for Transportation Data
```python
# Search for transportation-related datasets
search_datasets(
    query="transport roads traffic", 
    category="Transportation",
    limit=10
)
```

### Query Road Network Features
```python
# Query roads in a specific area
spatial_query_by_coordinates(
    service_url="https://services1.arcgis.com/.../FeatureServer/",
    xmin=30.8, ymin=-29.9,  # Durban area coordinates
    xmax=31.1, ymax=-29.7,
    max_records=50
)
```

### Get Statistical Information
```python
# Get statistics for a numeric field
get_layer_statistics(
    service_url="https://services1.arcgis.com/.../FeatureServer/",
    field_name="POPULATION",
    statistic_type="sum",
    where="DISTRICT='eThekwini'"
)
```

### Advanced Feature Querying
```python
# Query with attribute and spatial filters
query_feature_layer(
    service_url="https://services3.arcgis.com/HO0zfySJshlD6Twu/arcgis/rest/services/Roads/FeatureServer/",
    layer_id=0,
    where="STATUS='Active' AND CATEGORY='Residential'",
    return_geometry=True,
    max_records=100,
    out_fields="NAME,STATUS,CATEGORY,POPULATION"
)
```

### Working with Leases Dataset (Verified)
```python
# Query the eThekwini Leases dataset - this is working!
query_leases_dataset(
    where="SUBURB='Durban'",
    layer_id=11,
    format="geojson", 
    max_records=20
)

# Returns GeoJSON with properties including:
# OBJECTID, PROPKEY, SUBURB, STRNAME, LEASENUM, FARMTOWNNA, ERF, etc.
```

### Real Dataset Examples
The MCP server has discovered 141+ real datasets including:
- **Leases**: Property lease information with 24 fields
- **Roads**: Road network data  
- **Wards**: Municipal ward boundaries
- **Schools**: Educational institutions
- **Hospitals**: Healthcare facilities
- **Wetlands**: Environmental protection areas
- **Fire_Stations**: Emergency services locations
- **Libraries**: Public library locations
- **Zoning**: Land use zoning information

## Data Sources

This MCP server accesses data from:
- **eThekwini Open Data Portal**: [https://gis-ethekwini.opendata.arcgis.com](https://gis-ethekwini.opendata.arcgis.com)
- **ArcGIS REST Services**: Feature services, map services, and geoprocessing services
- **Municipal Datasets**: Transportation, environment, planning, utilities, and administrative data

## Auto-Discovery Mechanism

### How New APIs Are Detected

The MCP server uses several mechanisms to discover new datasets and APIs:

1. **Periodic Refresh**: Automatically refreshes dataset cache every 15 minutes
2. **Manual Refresh**: Use the `refresh_datasets` tool to manually update the cache
3. **API Monitoring**: Monitors the eThekwini open data API for new items
4. **Service Discovery**: Automatically detects and catalogs new ArcGIS REST services

### Cache Management

- **Cache Duration**: 15 minutes by default (configurable)
- **Force Refresh**: Manual refresh ignores cache timeout
- **Incremental Updates**: Only fetches new/updated datasets when possible
- **Error Handling**: Graceful fallback to cached data on API errors

### New Dataset Integration

When new datasets are added to the eThekwini portal:

1. **Automatic Detection**: Detected on next cache refresh cycle
2. **Tool Generation**: New tools may be dynamically generated for specific datasets
3. **Resource Registration**: New resources are automatically registered with the MCP
4. **Metadata Extraction**: Service information and schema are automatically discovered

## API Coverage

### Currently Supported Services
- **Feature Services**: Vector data with full query capabilities
- **Map Services**: Raster and cached map services
- **Geoprocessing Services**: Spatial analysis and processing tools
- **Image Services**: Aerial imagery and satellite data

### Service Types
- Transportation networks (roads, public transport)
- Administrative boundaries (wards, districts)
- Environmental data (air quality, green spaces)
- Utilities infrastructure (water, electricity)
- Planning and zoning information
- Census and demographic data

## Technical Architecture

### Components
- **MCP Server**: Core protocol implementation
- **Dataset Discovery Engine**: Automatic service discovery and cataloging  
- **Query Engine**: Spatial and attribute query processing
- **Cache Manager**: Intelligent caching with refresh logic
- **Error Handler**: Robust error handling and fallback mechanisms

### Performance Optimizations
- **Concurrent Requests**: Parallel API calls for faster discovery
- **Smart Caching**: Reduces API calls and improves response times
- **Query Optimization**: Efficient parameter handling and result processing
- **Connection Pooling**: Reuses HTTP connections for better performance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- eThekwini Municipality for providing open access to GIS data
- Esri for the ArcGIS REST API and open data platform
- Model Context Protocol (MCP) community for the protocol specification

## Support

For issues, questions, or contributions, please visit our [GitHub repository](https://github.com/bonnie-mapipa/ethekwini-gis-mcp) or open an issue.

---

**Note**: This MCP server is designed to work with publicly available data from eThekwini's open data portal. Ensure compliance with the municipality's data usage policies and terms of service.