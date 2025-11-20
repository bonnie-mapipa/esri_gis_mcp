# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-19

### Added
- Initial release of eThekwini ESRI GIS MCP server
- Automatic discovery of 142+ eThekwini municipality datasets
- 9 comprehensive tools for GIS data interaction:
  - `discover_datasets` - Auto-discover available datasets
  - `search_datasets` - Search datasets by keywords
  - `get_service_info` - Get detailed service information
  - `query_features` - Query spatial features with filters
  - `get_layer_info` - Get layer metadata and schema
  - `query_statistics` - Perform statistical analysis
  - `refresh_datasets` - Manual cache refresh
  - `buffer_query` - Spatial buffer queries
  - `export_features` - Export data in multiple formats

### Features
- **Auto-Discovery**: Intelligent dataset discovery with 15-minute cache refresh
- **Smart Search**: Full-text search across dataset names, descriptions, and metadata
- **Spatial Queries**: Support for complex spatial and attribute filtering
- **Statistical Analysis**: Built-in statistical functions (count, sum, min, max, avg, stddev)
- **Multiple Export Formats**: GeoJSON, Shapefile, KML, and CSV export support
- **Robust Error Handling**: Comprehensive error handling and fallback mechanisms
- **Performance Optimization**: Concurrent API calls and intelligent caching

### Technical Implementation
- Built on Model Context Protocol (MCP) v1.0+
- Python 3.8+ compatibility
- Async HTTP client with connection pooling
- RESTful ArcGIS API integration
- Comprehensive test suite with 100% pass rate

### Data Coverage
Successfully integrates with eThekwini municipality's open data including:
- **Municipal Services**: Leases, Zoning, Municipal Offices, Wards
- **Infrastructure**: Roads, Railways, Stormwater Systems, Utilities
- **Environmental Data**: Wetlands, Coastal Zones, Flood Plains, Green Spaces
- **Public Safety**: Fire Stations, Police Stations, Hospitals, Clinics
- **Community Services**: Libraries, Schools, Community Halls, Recreation
- **Planning Data**: Building Footprints, Land Use, Development Boundaries
- **Climate & Environment**: Drought Monitoring, Heat Stress, Air Quality

### Documentation
- Comprehensive README with installation and usage instructions
- API documentation with examples
- Contributing guidelines
- MIT License
- Full test coverage

### Configuration
- Environment variable support for customization
- Configurable refresh intervals and timeouts
- MCP client integration examples
- Cross-platform startup scripts (Windows/Linux/macOS)