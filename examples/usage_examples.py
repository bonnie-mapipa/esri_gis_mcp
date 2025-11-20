"""
Example usage of eThekwini GIS MCP Server
This demonstrates how to interact with the MCP server programmatically
"""

import asyncio
import json
from typing import Dict, List, Any

class MCPClient:
    """Simple MCP client for demonstration purposes"""
    
    def __init__(self, server):
        self.server = server
    
    async def list_resources(self) -> List[Dict]:
        """List all available resources"""
        return await self.server._list_resources()
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the server"""
        return await self.server._call_tool(name, arguments)

async def example_search_datasets():
    """Example: Search for transportation datasets"""
    print("🔍 Example: Searching for transportation datasets")
    
    # This would normally connect to the actual MCP server
    # For demo purposes, we'll simulate the calls
    
    search_results = {
        "query": "transportation roads traffic",
        "results": [
            {
                "id": "roads_network_2024",
                "name": "eThekwini Road Network 2024",
                "description": "Complete road network for eThekwini municipality including highways, arterials, and local roads",
                "type": "Feature Service",
                "categories": ["Transportation", "Infrastructure"],
                "url": "https://services1.arcgis.com/.../RoadNetwork/FeatureServer"
            },
            {
                "id": "traffic_signals_2024", 
                "name": "Traffic Signal Locations",
                "description": "Locations and operational status of traffic signals",
                "type": "Feature Service",
                "categories": ["Transportation", "Safety"],
                "url": "https://services1.arcgis.com/.../TrafficSignals/FeatureServer"
            }
        ]
    }
    
    print(f"Found {len(search_results['results'])} datasets:")
    for dataset in search_results['results']:
        print(f"  📊 {dataset['name']}")
        print(f"     Type: {dataset['type']}")
        print(f"     Categories: {', '.join(dataset['categories'])}")
        print()

async def example_spatial_query():
    """Example: Query features in Durban city center"""
    print("🗺️  Example: Spatial query for Durban city center")
    
    # Durban city center approximate coordinates
    durban_bbox = {
        "xmin": 31.0217,  # West longitude
        "ymin": -29.8669, # South latitude  
        "xmax": 31.0497,  # East longitude
        "ymax": -29.8469  # North latitude
    }
    
    # Simulated query result
    query_result = {
        "features": [
            {
                "attributes": {
                    "OBJECTID": 1,
                    "NAME": "Dr Pixley Kaseme Street",
                    "ROAD_TYPE": "Arterial",
                    "STATUS": "Active",
                    "LENGTH_M": 1250.5
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[31.0317, -29.8569], [31.0397, -29.8519]]
                }
            },
            {
                "attributes": {
                    "OBJECTID": 2,
                    "NAME": "Anton Lembede Street",
                    "ROAD_TYPE": "Arterial", 
                    "STATUS": "Active",
                    "LENGTH_M": 890.2
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[31.0247, -29.8589], [31.0327, -29.8539]]
                }
            }
        ],
        "count": 2
    }
    
    print(f"Query bounds: {durban_bbox}")
    print(f"Found {query_result['count']} features:")
    
    for feature in query_result['features']:
        attrs = feature['attributes']
        print(f"  🛣️  {attrs['NAME']}")
        print(f"     Type: {attrs['ROAD_TYPE']}")
        print(f"     Length: {attrs['LENGTH_M']:.1f}m")
        print()

async def example_statistics():
    """Example: Get statistics for road lengths"""
    print("📊 Example: Getting road length statistics")
    
    # Simulated statistics result
    stats_result = {
        "features": [{
            "attributes": {
                "count_LENGTH_M": 1245,
                "sum_LENGTH_M": 2847392.7,
                "avg_LENGTH_M": 288.4,
                "min_LENGTH_M": 12.3,
                "max_LENGTH_M": 15847.2,
                "stddev_LENGTH_M": 445.8
            }
        }]
    }
    
    stats = stats_result['features'][0]['attributes']
    
    print("Road network statistics:")
    print(f"  Total roads: {stats['count_LENGTH_M']:,}")
    print(f"  Total length: {stats['sum_LENGTH_M']:,.1f} meters ({stats['sum_LENGTH_M']/1000:.1f} km)")
    print(f"  Average length: {stats['avg_LENGTH_M']:.1f} meters")
    print(f"  Shortest road: {stats['min_LENGTH_M']:.1f} meters")
    print(f"  Longest road: {stats['max_LENGTH_M']:,.1f} meters")
    print(f"  Standard deviation: {stats['stddev_LENGTH_M']:.1f} meters")

async def example_municipal_services():
    """Example: List municipal service categories"""
    print("🏛️  Example: Municipal service categories")
    
    # Simulated municipal services data
    services_data = {
        "categories": {
            "Transportation": [
                "Road Network 2024",
                "Traffic Signals", 
                "Bus Routes",
                "Taxi Ranks",
                "Parking Areas"
            ],
            "Environment": [
                "Air Quality Monitoring",
                "Green Spaces",
                "Waste Collection Points",
                "Water Quality",
                "Protected Areas"
            ],
            "Infrastructure": [
                "Water Infrastructure", 
                "Electricity Grid",
                "Telecommunications",
                "Storm Water",
                "Sewerage Network"
            ],
            "Planning": [
                "Zoning Information",
                "Land Use",
                "Development Applications", 
                "Building Plans",
                "Property Boundaries"
            ]
        },
        "service_types": {
            "Feature Service": 23,
            "Map Service": 12,
            "Image Service": 5,
            "Geoprocessing Service": 3
        },
        "total_datasets": 43,
        "total_services": 43
    }
    
    print(f"Total datasets: {services_data['total_datasets']}")
    print(f"Total services: {services_data['total_services']}")
    print()
    
    print("Service categories:")
    for category, datasets in services_data['categories'].items():
        print(f"  📂 {category} ({len(datasets)} datasets)")
        for dataset in datasets[:3]:  # Show first 3
            print(f"    - {dataset}")
        if len(datasets) > 3:
            print(f"    ... and {len(datasets) - 3} more")
        print()
    
    print("Service types:")
    for service_type, count in services_data['service_types'].items():
        print(f"  🔧 {service_type}: {count}")

async def example_field_information():
    """Example: Get field information for a layer"""
    print("📋 Example: Layer field information")
    
    # Simulated field information
    field_info = {
        "layer_name": "eThekwini Road Network",
        "layer_description": "Complete road network for eThekwini municipality",
        "geometry_type": "esriGeometryPolyline",
        "fields": [
            {
                "name": "OBJECTID",
                "type": "esriFieldTypeOID", 
                "alias": "Object ID",
                "nullable": False,
                "editable": False
            },
            {
                "name": "ROAD_NAME",
                "type": "esriFieldTypeString",
                "alias": "Road Name",
                "length": 100,
                "nullable": True,
                "editable": True
            },
            {
                "name": "ROAD_TYPE",
                "type": "esriFieldTypeString", 
                "alias": "Road Type",
                "length": 50,
                "nullable": True,
                "editable": True
            },
            {
                "name": "STATUS",
                "type": "esriFieldTypeString",
                "alias": "Status",
                "length": 20,
                "nullable": True,
                "editable": True
            },
            {
                "name": "LENGTH_M",
                "type": "esriFieldTypeDouble",
                "alias": "Length (meters)",
                "nullable": True,
                "editable": True
            },
            {
                "name": "SURFACE_TYPE",
                "type": "esriFieldTypeString",
                "alias": "Surface Type", 
                "length": 30,
                "nullable": True,
                "editable": True
            }
        ]
    }
    
    print(f"Layer: {field_info['layer_name']}")
    print(f"Description: {field_info['layer_description']}")
    print(f"Geometry Type: {field_info['geometry_type']}")
    print()
    
    print("Fields:")
    for field in field_info['fields']:
        field_desc = f"  📝 {field['name']} ({field['alias']})"
        field_desc += f" - {field['type']}"
        if 'length' in field:
            field_desc += f"({field['length']})"
        if not field['nullable']:
            field_desc += " [Required]"
        print(field_desc)

async def run_all_examples():
    """Run all example demonstrations"""
    print("🎯 eThekwini GIS MCP Server - Usage Examples")
    print("=" * 60)
    
    examples = [
        example_search_datasets,
        example_spatial_query,
        example_statistics,
        example_municipal_services,
        example_field_information
    ]
    
    for i, example_func in enumerate(examples, 1):
        print(f"\n[Example {i}/{len(examples)}]")
        print("-" * 40)
        await example_func()
        
        if i < len(examples):
            print("\n" + "⏳ " * 20)
            await asyncio.sleep(1)  # Small delay between examples
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("\nTo use these features with the actual MCP server:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run server: python src/ethekwini_gis_mcp.py")
    print("3. Configure your MCP client with mcp-config.json")
    print("4. Use the tools shown in these examples")

if __name__ == "__main__":
    asyncio.run(run_all_examples())