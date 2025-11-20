"""
eThekwini ESRI GIS Model Context Protocol (MCP) Server
Provides access to eThekwini municipality's open GIS data portal
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urljoin, urlparse, parse_qs
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Version information
__version__ = "1.0.0"
__author__ = "eThekwini GIS MCP Contributors"

import mcp.server.stdio
import mcp.types as types
import re

# Configure logging with environment variable support
log_level = os.getenv("ETHEKWINI_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ethekwini-gis-mcp")

# Log startup information
logger.info(f"eThekwini GIS MCP Server v{__version__} starting up...")

class EThekwiniGISServer:
    def __init__(self):
        self.base_url = "https://gis-ethekwini.opendata.arcgis.com"
        self.api_base = "https://services3.arcgis.com/HO0zfySJshlD6Twu/arcgis/rest/services"
        self.server = Server("ethekwini-gis-mcp")
        self.client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        self.cached_datasets = {}
        self.cached_services = {}
        self.last_refresh = None
        self.group_id = "bc9877523e074449bae4dcdb6a118e12"
        
        # Known service endpoints from eThekwini
        self.known_services = {
            "Leases": "https://services3.arcgis.com/HO0zfySJshlD6Twu/arcgis/rest/services/Leases/FeatureServer",
            # Add more as discovered
        }
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available eThekwini GIS resources"""
            await self._refresh_datasets()
            
            resources = []
            
            # Add dataset resources
            for dataset_id, dataset_info in self.cached_datasets.items():
                resources.append(Resource(
                    uri=f"ethekwini-gis://dataset/{dataset_id}",
                    name=f"Dataset: {dataset_info.get('name', dataset_id)}",
                    description=dataset_info.get('description', 'eThekwini GIS Dataset'),
                    mimeType="application/json"
                ))
            
            # Add service resources
            for service_name, service_info in self.cached_services.items():
                resources.append(Resource(
                    uri=f"ethekwini-gis://service/{service_name}",
                    name=f"Service: {service_name}",
                    description=service_info.get('description', 'eThekwini GIS Service'),
                    mimeType="application/json"
                ))
            
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read eThekwini GIS resource details"""
            if not uri.startswith("ethekwini-gis://"):
                raise ValueError(f"Unsupported URI scheme: {uri}")
            
            parts = uri.replace("ethekwini-gis://", "").split("/")
            resource_type = parts[0]
            resource_id = parts[1] if len(parts) > 1 else ""
            
            await self._refresh_datasets()
            
            if resource_type == "dataset" and resource_id in self.cached_datasets:
                return json.dumps(self.cached_datasets[resource_id], indent=2)
            elif resource_type == "service" and resource_id in self.cached_services:
                return json.dumps(self.cached_services[resource_id], indent=2)
            else:
                raise ValueError(f"Resource not found: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available eThekwini GIS tools"""
            await self._refresh_datasets()
            
            tools = [
                Tool(
                    name="refresh_datasets",
                    description="Refresh and discover eThekwini GIS datasets and services",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="search_datasets",
                    description="Search eThekwini datasets by keyword, category, or tag",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (keywords, tags, or categories)"
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by category (e.g., 'Transportation', 'Environment')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 20
                            }
                        }
                    }
                ),
                Tool(
                    name="get_dataset_info",
                    description="Get detailed information about a specific dataset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "Dataset ID or name"
                            }
                        },
                        "required": ["dataset_id"]
                    }
                ),
                Tool(
                    name="query_feature_layer",
                    description="Query features from a dataset's feature layer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service_url": {
                                "type": "string",
                                "description": "Feature service URL"
                            },
                            "layer_id": {
                                "type": "integer", 
                                "description": "Layer ID (default: 0)",
                                "default": 0
                            },
                            "where": {
                                "type": "string",
                                "description": "SQL WHERE clause for filtering",
                                "default": "1=1"
                            },
                            "geometry": {
                                "type": "string",
                                "description": "Geometry for spatial filtering (WKT or JSON)"
                            },
                            "spatial_rel": {
                                "type": "string",
                                "description": "Spatial relationship (intersects, contains, within, etc.)",
                                "default": "esriSpatialRelIntersects"
                            },
                            "return_geometry": {
                                "type": "boolean",
                                "description": "Include geometry in results",
                                "default": True
                            },
                            "max_records": {
                                "type": "integer",
                                "description": "Maximum records to return",
                                "default": 100
                            },
                            "out_fields": {
                                "type": "string",
                                "description": "Comma-separated list of fields to return (* for all)",
                                "default": "*"
                            }
                        },
                        "required": ["service_url"]
                    }
                ),
                Tool(
                    name="get_layer_statistics",
                    description="Get statistics for numeric fields in a layer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service_url": {
                                "type": "string",
                                "description": "Feature service URL"
                            },
                            "layer_id": {
                                "type": "integer",
                                "description": "Layer ID",
                                "default": 0
                            },
                            "field_name": {
                                "type": "string",
                                "description": "Field name for statistics"
                            },
                            "statistic_type": {
                                "type": "string",
                                "description": "Type of statistic (count, sum, min, max, avg, stddev)",
                                "default": "count"
                            },
                            "where": {
                                "type": "string", 
                                "description": "WHERE clause for filtering",
                                "default": "1=1"
                            }
                        },
                        "required": ["service_url", "field_name"]
                    }
                ),
                Tool(
                    name="list_municipal_services",
                    description="List available municipal service categories",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_layer_fields",
                    description="Get field information for a feature layer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service_url": {
                                "type": "string",
                                "description": "Feature service URL"
                            },
                            "layer_id": {
                                "type": "integer",
                                "description": "Layer ID",
                                "default": 0
                            }
                        },
                        "required": ["service_url"]
                    }
                ),
                Tool(
                    name="spatial_query_by_coordinates",
                    description="Query features within a bounding box or near coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service_url": {
                                "type": "string",
                                "description": "Feature service URL"
                            },
                            "layer_id": {
                                "type": "integer",
                                "description": "Layer ID",
                                "default": 0
                            },
                            "xmin": {
                                "type": "number",
                                "description": "Minimum X coordinate (longitude)"
                            },
                            "ymin": {
                                "type": "number",
                                "description": "Minimum Y coordinate (latitude)"
                            },
                            "xmax": {
                                "type": "number",
                                "description": "Maximum X coordinate (longitude)"
                            },
                            "ymax": {
                                "type": "number",
                                "description": "Maximum Y coordinate (latitude)"
                            },
                            "buffer_distance": {
                                "type": "number",
                                "description": "Buffer distance in meters for point queries"
                            },
                            "max_records": {
                                "type": "integer",
                                "description": "Maximum records to return",
                                "default": 100
                            }
                        },
                        "required": ["service_url", "xmin", "ymin", "xmax", "ymax"]
                    }
                ),
                Tool(
                    name="add_known_service",
                    description="Add a known eThekwini service URL to the server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Name for the service"
                            },
                            "service_url": {
                                "type": "string",
                                "description": "Full URL to the ArcGIS service"
                            }
                        },
                        "required": ["service_name", "service_url"]
                    }
                ),
                Tool(
                    name="query_leases_dataset",
                    description="Query the eThekwini Leases dataset with specific filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "where": {
                                "type": "string",
                                "description": "SQL WHERE clause for filtering leases",
                                "default": "1=1"
                            },
                            "layer_id": {
                                "type": "integer",
                                "description": "Layer ID in the Leases service",
                                "default": 11
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format (json, geojson)",
                                "default": "geojson"
                            },
                            "max_records": {
                                "type": "integer",
                                "description": "Maximum records to return",
                                "default": 100
                            }
                        }
                    }
                )
            ]
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "refresh_datasets":
                    await self._refresh_datasets(force=True)
                    return [types.TextContent(
                        type="text",
                        text=f"Refreshed datasets. Found {len(self.cached_datasets)} datasets and {len(self.cached_services)} services."
                    )]
                
                elif name == "search_datasets":
                    results = await self._search_datasets(
                        query=arguments.get("query", ""),
                        category=arguments.get("category"),
                        limit=arguments.get("limit", 20)
                    )
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(results, indent=2)
                    )]
                
                elif name == "get_dataset_info":
                    result = await self._get_dataset_info(arguments["dataset_id"])
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "query_feature_layer":
                    result = await self._query_feature_layer(
                        service_url=arguments["service_url"],
                        layer_id=arguments.get("layer_id", 0),
                        where=arguments.get("where", "1=1"),
                        geometry=arguments.get("geometry"),
                        spatial_rel=arguments.get("spatial_rel", "esriSpatialRelIntersects"),
                        return_geometry=arguments.get("return_geometry", True),
                        max_records=arguments.get("max_records", 100),
                        out_fields=arguments.get("out_fields", "*")
                    )
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "get_layer_statistics":
                    result = await self._get_layer_statistics(
                        service_url=arguments["service_url"],
                        layer_id=arguments.get("layer_id", 0),
                        field_name=arguments["field_name"],
                        statistic_type=arguments.get("statistic_type", "count"),
                        where=arguments.get("where", "1=1")
                    )
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "list_municipal_services":
                    result = await self._list_municipal_services()
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "get_layer_fields":
                    result = await self._get_layer_fields(
                        service_url=arguments["service_url"],
                        layer_id=arguments.get("layer_id", 0)
                    )
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "spatial_query_by_coordinates":
                    result = await self._spatial_query_by_coordinates(
                        service_url=arguments["service_url"],
                        layer_id=arguments.get("layer_id", 0),
                        xmin=arguments["xmin"],
                        ymin=arguments["ymin"],
                        xmax=arguments["xmax"],
                        ymax=arguments["ymax"],
                        buffer_distance=arguments.get("buffer_distance"),
                        max_records=arguments.get("max_records", 100)
                    )
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "add_known_service":
                    result = await self._add_known_service(
                        service_name=arguments["service_name"],
                        service_url=arguments["service_url"]
                    )
                    return [types.TextContent(
                        type="text",
                        text=result
                    )]
                
                elif name == "query_leases_dataset":
                    result = await self._query_leases_dataset(
                        where=arguments.get("where", "1=1"),
                        layer_id=arguments.get("layer_id", 11),
                        format=arguments.get("format", "geojson"),
                        max_records=arguments.get("max_records", 100)
                    )
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _refresh_datasets(self, force: bool = False):
        """Discover and cache eThekwini GIS datasets"""
        import time
        
        # Skip refresh if recently done (unless forced)
        if not force and self.last_refresh and (time.time() - self.last_refresh) < 900:  # 15 minutes
            return
        
        try:
            logger.info("Discovering eThekwini GIS services...")
            
            all_datasets = {}
            all_services = {}
            
            # Start with known services
            for service_name, service_url in self.known_services.items():
                try:
                    service_info = await self._get_service_info(service_url)
                    if service_info:
                        dataset_info = {
                            "id": service_name.lower(),
                            "name": service_name,
                            "title": service_info.get("serviceDescription", service_name),
                            "description": service_info.get("description", f"{service_name} feature service from eThekwini municipality"),
                            "type": "Feature Service",
                            "url": service_url,
                            "created": "",
                            "updated": "",
                            "tags": ["eThekwini", "municipality", "GIS"],
                            "categories": ["Municipal Services"],
                            "owner": {"name": "eThekwini Municipality"},
                            "service_info": service_info,
                            "layers": service_info.get("layers", [])
                        }
                        
                        all_datasets[service_name.lower()] = dataset_info
                        all_services[service_name] = {
                            "name": service_name,
                            "url": service_url,
                            "type": "Feature Service",
                            "dataset_id": service_name.lower(),
                            "info": service_info
                        }
                        
                        logger.info(f"Added service: {service_name} with {len(service_info.get('layers', []))} layers")
                        
                except Exception as e:
                    logger.warning(f"Could not get info for service {service_name}: {e}")
            
            # Try to discover more services from the main services endpoint
            try:
                services_response = await self.client.get(f"{self.api_base}?f=json")
                if services_response.status_code == 200:
                    services_data = services_response.json()
                    
                    # Add root level services
                    for service in services_data.get("services", []):
                        service_name = service.get("name", "")
                        service_type = service.get("type", "")
                        
                        if service_type in ["FeatureServer", "MapServer"] and service_name not in self.known_services:
                            service_url = f"{self.api_base}/{service_name}/{service_type}"
                            
                            try:
                                service_info = await self._get_service_info(service_url)
                                if service_info:
                                    dataset_info = {
                                        "id": service_name.lower(),
                                        "name": service_name,
                                        "title": service_info.get("serviceDescription", service_name),
                                        "description": service_info.get("description", f"{service_name} service from eThekwini municipality"),
                                        "type": service_type,
                                        "url": service_url,
                                        "created": "",
                                        "updated": "",
                                        "tags": ["eThekwini", "municipality", "GIS"],
                                        "categories": ["Municipal Services"],
                                        "owner": {"name": "eThekwini Municipality"},
                                        "service_info": service_info,
                                        "layers": service_info.get("layers", [])
                                    }
                                    
                                    all_datasets[service_name.lower()] = dataset_info
                                    all_services[service_name] = {
                                        "name": service_name,
                                        "url": service_url,
                                        "type": service_type,
                                        "dataset_id": service_name.lower(),
                                        "info": service_info
                                    }
                                    
                                    logger.info(f"Discovered service: {service_name} ({service_type})")
                                    
                            except Exception as e:
                                logger.debug(f"Could not get info for discovered service {service_name}: {e}")
                    
                    # Add folder services
                    for folder in services_data.get("folders", []):
                        try:
                            folder_response = await self.client.get(f"{self.api_base}/{folder}?f=json")
                            if folder_response.status_code == 200:
                                folder_data = folder_response.json()
                                
                                for service in folder_data.get("services", []):
                                    service_name = service.get("name", "")
                                    service_type = service.get("type", "")
                                    full_service_name = f"{folder}/{service_name}"
                                    
                                    if service_type in ["FeatureServer", "MapServer"]:
                                        service_url = f"{self.api_base}/{full_service_name}/{service_type}"
                                        
                                        try:
                                            service_info = await self._get_service_info(service_url)
                                            if service_info:
                                                dataset_info = {
                                                    "id": full_service_name.lower().replace("/", "_"),
                                                    "name": full_service_name,
                                                    "title": service_info.get("serviceDescription", service_name),
                                                    "description": service_info.get("description", f"{service_name} service from eThekwini municipality"),
                                                    "type": service_type,
                                                    "url": service_url,
                                                    "created": "",
                                                    "updated": "",
                                                    "tags": ["eThekwini", "municipality", "GIS", folder],
                                                    "categories": ["Municipal Services", folder],
                                                    "owner": {"name": "eThekwini Municipality"},
                                                    "service_info": service_info,
                                                    "layers": service_info.get("layers", [])
                                                }
                                                
                                                all_datasets[full_service_name.lower().replace("/", "_")] = dataset_info
                                                all_services[full_service_name] = {
                                                    "name": full_service_name,
                                                    "url": service_url,
                                                    "type": service_type,
                                                    "dataset_id": full_service_name.lower().replace("/", "_"),
                                                    "info": service_info
                                                }
                                                
                                                logger.info(f"Discovered folder service: {full_service_name} ({service_type})")
                                                
                                        except Exception as e:
                                            logger.debug(f"Could not get info for folder service {full_service_name}: {e}")
                        except Exception as e:
                            logger.debug(f"Could not process folder {folder}: {e}")
                            
            except Exception as e:
                logger.warning(f"Could not discover additional services: {e}")
            
            self.cached_datasets = all_datasets
            self.cached_services = all_services
            self.last_refresh = time.time()
            
            logger.info(f"Discovered {len(all_datasets)} datasets and {len(all_services)} services")
            
        except Exception as e:
            logger.error(f"Error refreshing datasets: {e}")
            # Don't raise, allow fallback to cached data
    
    async def _search_datasets(self, query: str = "", category: str = None, limit: int = 20) -> List[Dict]:
        """Search datasets by query and category"""
        await self._refresh_datasets()
        
        results = []
        query_lower = query.lower() if query else ""
        
        for dataset_id, dataset_info in self.cached_datasets.items():
            # Check if dataset matches search criteria
            matches = True
            
            if query:
                searchable_text = " ".join([
                    dataset_info.get("name", ""),
                    dataset_info.get("title", ""),
                    dataset_info.get("description", ""),
                    " ".join(dataset_info.get("tags", []))
                ]).lower()
                
                if query_lower not in searchable_text:
                    matches = False
            
            if category and matches:
                dataset_categories = [cat.lower() for cat in dataset_info.get("categories", [])]
                if category.lower() not in dataset_categories:
                    matches = False
            
            if matches:
                results.append(dataset_info)
                if len(results) >= limit:
                    break
        
        return results
    
    async def _get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """Get detailed information about a dataset"""
        await self._refresh_datasets()
        
        # Try by ID first
        if dataset_id in self.cached_datasets:
            return self.cached_datasets[dataset_id]
        
        # Try by name
        for cached_id, dataset_info in self.cached_datasets.items():
            if (dataset_info.get("name", "").lower() == dataset_id.lower() or 
                dataset_info.get("title", "").lower() == dataset_id.lower()):
                return dataset_info
        
        raise ValueError(f"Dataset not found: {dataset_id}")
    
    async def _query_feature_layer(self, service_url: str, layer_id: int = 0,
                                 where: str = "1=1", geometry: str = None,
                                 spatial_rel: str = "esriSpatialRelIntersects",
                                 return_geometry: bool = True, max_records: int = 100,
                                 out_fields: str = "*") -> Dict[str, Any]:
        """Query features from a feature layer"""
        
        # Construct query URL
        if not service_url.endswith('/'):
            service_url += '/'
        query_url = f"{service_url}{layer_id}/query"
        
        params = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": str(return_geometry).lower(),
            "f": "json",
            "resultRecordCount": max_records,
            "spatialRel": spatial_rel
        }
        
        if geometry:
            params["geometry"] = geometry
            params["geometryType"] = "esriGeometryPolygon"  # Assume polygon, adjust as needed
        
        response = await self.client.get(query_url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    async def _get_layer_statistics(self, service_url: str, layer_id: int = 0,
                                  field_name: str = "", statistic_type: str = "count",
                                  where: str = "1=1") -> Dict[str, Any]:
        """Get statistics for a field in a layer"""
        
        if not service_url.endswith('/'):
            service_url += '/'
        query_url = f"{service_url}{layer_id}/query"
        
        out_statistics = [{
            "statisticType": statistic_type,
            "onStatisticField": field_name,
            "outStatisticFieldName": f"{statistic_type}_{field_name}"
        }]
        
        params = {
            "where": where,
            "outStatistics": json.dumps(out_statistics),
            "f": "json"
        }
        
        response = await self.client.get(query_url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    async def _get_service_info(self, service_url: str) -> Dict[str, Any]:
        """Get information about a service"""
        try:
            params = {"f": "json"}
            response = await self.client.get(service_url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None
    
    async def _list_municipal_services(self) -> Dict[str, Any]:
        """List municipal service categories available in the data"""
        await self._refresh_datasets()
        
        categories = {}
        service_types = {}
        
        for dataset_id, dataset_info in self.cached_datasets.items():
            # Collect categories
            for category in dataset_info.get("categories", []):
                if category not in categories:
                    categories[category] = []
                categories[category].append(dataset_info["name"])
            
            # Collect service types
            service_type = dataset_info.get("type", "Unknown")
            if service_type not in service_types:
                service_types[service_type] = 0
            service_types[service_type] += 1
        
        return {
            "categories": categories,
            "service_types": service_types,
            "total_datasets": len(self.cached_datasets),
            "total_services": len(self.cached_services)
        }
    
    async def _get_layer_fields(self, service_url: str, layer_id: int = 0) -> Dict[str, Any]:
        """Get field information for a feature layer"""
        
        if not service_url.endswith('/'):
            service_url += '/'
        layer_url = f"{service_url}{layer_id}"
        
        params = {"f": "json"}
        
        response = await self.client.get(layer_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract field information
        fields_info = {
            "layer_name": data.get("name", ""),
            "layer_description": data.get("description", ""),
            "geometry_type": data.get("geometryType", ""),
            "fields": []
        }
        
        for field in data.get("fields", []):
            fields_info["fields"].append({
                "name": field.get("name", ""),
                "type": field.get("type", ""),
                "alias": field.get("alias", ""),
                "length": field.get("length"),
                "nullable": field.get("nullable", True),
                "editable": field.get("editable", False)
            })
        
        return fields_info
    
    async def _spatial_query_by_coordinates(self, service_url: str, layer_id: int = 0,
                                          xmin: float = 0, ymin: float = 0,
                                          xmax: float = 0, ymax: float = 0,
                                          buffer_distance: float = None,
                                          max_records: int = 100) -> Dict[str, Any]:
        """Query features within a bounding box or buffer around coordinates"""
        
        if not service_url.endswith('/'):
            service_url += '/'
        query_url = f"{service_url}{layer_id}/query"
        
        # Create geometry envelope
        geometry = {
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
            "spatialReference": {"wkid": 4326}  # WGS84
        }
        
        params = {
            "geometry": json.dumps(geometry),
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "json",
            "resultRecordCount": max_records
        }
        
        # Add buffer if specified
        if buffer_distance:
            params["distance"] = buffer_distance
            params["units"] = "esriSRUnit_Meter"
        
        response = await self.client.get(query_url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    async def _add_known_service(self, service_name: str, service_url: str) -> str:
        """Add a known service to the server and refresh datasets"""
        try:
            # Add to known services
            self.known_services[service_name] = service_url
            
            # Refresh datasets to include the new service
            await self._refresh_datasets(force=True)
            
            return f"Successfully added service '{service_name}' at {service_url}. Found {len(self.cached_datasets)} total datasets."
        
        except Exception as e:
            return f"Error adding service '{service_name}': {str(e)}"
    
    async def _query_leases_dataset(self, where: str = "1=1", layer_id: int = 11, 
                                  format: str = "geojson", max_records: int = 100) -> Dict[str, Any]:
        """Query the eThekwini Leases dataset"""
        
        leases_url = "https://services3.arcgis.com/HO0zfySJshlD6Twu/arcgis/rest/services/Leases/FeatureServer"
        query_url = f"{leases_url}/{layer_id}/query"
        
        params = {
            "where": where,
            "outFields": "*",
            "f": format,
            "resultRecordCount": max_records
        }
        
        # Add geometry parameter for geojson format
        if format.lower() == "geojson":
            params["returnGeometry"] = "true"
        
        response = await self.client.get(query_url, params=params)
        response.raise_for_status()
        
        if format.lower() == "geojson":
            return response.json()
        else:
            return response.json()
    
    async def run(self):
        """Run the MCP server"""
        # Initial dataset discovery
        await self._refresh_datasets()
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ethekwini-gis-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    server = EThekwiniGISServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())