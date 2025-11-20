"""
Azure Function App for eThekwini GIS MCP
Provides REST API endpoints for Azure AI Foundry integration
"""

import azure.functions as func
import json
import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add the parent directory to Python path to import MCP server
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ethekwini_gis_mcp import EThekwiniGISServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ethekwini-gis-function")

# Initialize the function app with v2 programming model
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Global server instance (initialized on first request)
_server_instance: Optional[EThekwiniGISServer] = None

async def get_server_instance() -> EThekwiniGISServer:
    """Get or create server instance with lazy initialization"""
    global _server_instance
    if _server_instance is None:
        logger.info("Initializing eThekwini GIS server...")
        _server_instance = EThekwiniGISServer()
        # Pre-warm the datasets cache
        try:
            await _server_instance._refresh_datasets()
            logger.info(f"Server initialized with {len(_server_instance.datasets)} datasets")
        except Exception as e:
            logger.error(f"Failed to initialize datasets: {e}")
    return _server_instance

def create_response(data: Any, status_code: int = 200) -> func.HttpResponse:
    """Create standardized HTTP response with CORS headers"""
    return func.HttpResponse(
        json.dumps(data, indent=2, default=str),
        status_code=status_code,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
        }
    )

def handle_error(error: Exception, context: str) -> func.HttpResponse:
    """Handle errors consistently with proper logging"""
    error_msg = str(error)
    logger.error(f"Error in {context}: {error_msg}")
    return create_response({
        "error": error_msg,
        "context": context,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "error"
    }, 500)

# Health check endpoint
@app.function_name("health")
@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for monitoring"""
    try:
        server = await get_server_instance()
        return create_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "datasets_count": len(server.datasets),
            "version": "1.0.0"
        })
    except Exception as e:
        return handle_error(e, "health_check")

# List all available datasets
@app.function_name("list_datasets")
@app.route(route="datasets", methods=["GET"])
async def list_datasets(req: func.HttpRequest) -> func.HttpResponse:
    """List all available eThekwini GIS datasets"""
    try:
        server = await get_server_instance()
        
        # Get query parameters
        category = req.params.get('category')
        search = req.params.get('search')
        
        datasets = []
        for dataset_id, dataset_info in server.datasets.items():
            # Apply filters
            if category and category.lower() not in dataset_info.get('name', '').lower():
                continue
            if search and search.lower() not in dataset_info.get('name', '').lower():
                continue
                
            datasets.append({
                "id": dataset_id,
                "name": dataset_info.get('name', 'Unknown'),
                "description": dataset_info.get('description', ''),
                "geometry_type": dataset_info.get('geometryType', 'Unknown'),
                "max_record_count": dataset_info.get('maxRecordCount', 1000)
            })
        
        return create_response({
            "datasets": datasets,
            "total_count": len(datasets),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "list_datasets")

# Get dataset information
@app.function_name("dataset_info")
@app.route(route="datasets/{dataset_id}/info", methods=["GET"])
async def get_dataset_info(req: func.HttpRequest) -> func.HttpResponse:
    """Get detailed information about a specific dataset"""
    try:
        server = await get_server_instance()
        dataset_id = req.route_params.get('dataset_id')
        
        if not dataset_id:
            return create_response({"error": "Dataset ID is required"}, 400)
        
        # Call the MCP tool
        result = await server.get_dataset_info(dataset_id)
        
        return create_response({
            "dataset_info": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "get_dataset_info")

# Query dataset data
@app.function_name("query_dataset")
@app.route(route="datasets/{dataset_id}/query", methods=["POST"])
async def query_dataset(req: func.HttpRequest) -> func.HttpResponse:
    """Query data from a specific dataset"""
    try:
        server = await get_server_instance()
        dataset_id = req.route_params.get('dataset_id')
        
        if not dataset_id:
            return create_response({"error": "Dataset ID is required"}, 400)
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        
        where_clause = req_body.get('where', '1=1')
        max_records = req_body.get('max_records', 10)
        fields = req_body.get('fields', '*')
        
        # Call the MCP tool
        result = await server.query_dataset(dataset_id, where_clause, max_records, fields)
        
        return create_response({
            "query_result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "query_dataset")

# Spatial query endpoint
@app.function_name("spatial_query")
@app.route(route="datasets/{dataset_id}/spatial", methods=["POST"])
async def spatial_query(req: func.HttpRequest) -> func.HttpResponse:
    """Perform spatial query on a dataset"""
    try:
        server = await get_server_instance()
        dataset_id = req.route_params.get('dataset_id')
        
        if not dataset_id:
            return create_response({"error": "Dataset ID is required"}, 400)
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_response({"error": "Invalid JSON in request body"}, 400)
        
        geometry = req_body.get('geometry')
        spatial_rel = req_body.get('spatial_rel', 'esriSpatialRelIntersects')
        max_records = req_body.get('max_records', 10)
        
        if not geometry:
            return create_response({"error": "Geometry is required for spatial query"}, 400)
        
        # Call the MCP tool
        result = await server.spatial_query(dataset_id, geometry, spatial_rel, max_records)
        
        return create_response({
            "spatial_result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "spatial_query")

# Search datasets
@app.function_name("search_datasets")
@app.route(route="search", methods=["GET", "POST"])
async def search_datasets(req: func.HttpRequest) -> func.HttpResponse:
    """Search for datasets by keyword"""
    try:
        server = await get_server_instance()
        
        # Get search term from query params or body
        if req.method == "GET":
            search_term = req.params.get('q', '')
        else:
            req_body = req.get_json() or {}
            search_term = req_body.get('search_term', req.params.get('q', ''))
        
        if not search_term:
            return create_response({"error": "Search term is required"}, 400)
        
        # Call the MCP tool
        result = await server.search_datasets(search_term)
        
        return create_response({
            "search_results": result,
            "search_term": search_term,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "search_datasets")

# Get dataset statistics
@app.function_name("dataset_stats")
@app.route(route="datasets/{dataset_id}/stats", methods=["GET"])
async def get_dataset_statistics(req: func.HttpRequest) -> func.HttpResponse:
    """Get statistical information about a dataset"""
    try:
        server = await get_server_instance()
        dataset_id = req.route_params.get('dataset_id')
        
        if not dataset_id:
            return create_response({"error": "Dataset ID is required"}, 400)
        
        # Call the MCP tool
        result = await server.get_dataset_statistics(dataset_id)
        
        return create_response({
            "statistics": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "get_dataset_statistics")

# Refresh datasets cache
@app.function_name("refresh_datasets")
@app.route(route="admin/refresh", methods=["POST"])
async def refresh_datasets(req: func.HttpRequest) -> func.HttpResponse:
    """Manually refresh the datasets cache (admin function)"""
    try:
        server = await get_server_instance()
        
        # Call the MCP tool
        result = await server.refresh_datasets()
        
        return create_response({
            "refresh_result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return handle_error(e, "refresh_datasets")

# CORS preflight handler
@app.function_name("cors_handler")
@app.route(route="{*path}", methods=["OPTIONS"])
async def handle_cors(req: func.HttpRequest) -> func.HttpResponse:
    """Handle CORS preflight requests"""
    return func.HttpResponse(
        "",
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "3600"
        }
    )

# API documentation endpoint
@app.function_name("api_docs")
@app.route(route="", methods=["GET"])
async def api_documentation(req: func.HttpRequest) -> func.HttpResponse:
    """API documentation and available endpoints"""
    
    docs = {
        "name": "eThekwini GIS MCP API",
        "version": "1.0.0",
        "description": "REST API for accessing eThekwini municipality GIS datasets",
        "endpoints": {
            "GET /health": "Health check",
            "GET /datasets": "List all datasets (supports ?category and ?search filters)",
            "GET /datasets/{id}/info": "Get dataset information",
            "POST /datasets/{id}/query": "Query dataset data",
            "POST /datasets/{id}/spatial": "Spatial query on dataset", 
            "GET|POST /search": "Search datasets by keyword",
            "GET /datasets/{id}/stats": "Get dataset statistics",
            "POST /admin/refresh": "Refresh datasets cache"
        },
        "example_usage": {
            "list_datasets": "GET /datasets?category=transport",
            "query_data": "POST /datasets/11/query with JSON body: {'where': 'STATUS=1', 'max_records': 20}",
            "spatial_query": "POST /datasets/11/spatial with JSON body: {'geometry': {...}, 'spatial_rel': 'esriSpatialRelWithin'}"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return create_response(docs)