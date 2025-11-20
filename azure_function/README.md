# eThekwini GIS MCP - Azure Function Deployment

This directory contains the Azure Function implementation of the eThekwini GIS MCP server, designed for integration with Azure AI Foundry agents and other cloud-based AI applications.

## 🌟 Features

- **REST API Interface** - HTTP endpoints for all MCP tools
- **Azure AI Foundry Ready** - Perfect for AI agent knowledge bases
- **Auto-scaling** - Consumption plan handles traffic spikes
- **CORS Enabled** - Ready for web applications
- **Health Monitoring** - Built-in health checks and monitoring
- **Secure** - Function-level authentication
- **South Africa Hosted** - Deployed in Johannesburg region for optimal performance

## 🏗️ Architecture

```
Azure AI Foundry Agent
         ↓
Azure Function App (REST API)
         ↓
eThekwini GIS MCP Server
         ↓
eThekwini ArcGIS Services
```

## 📚 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/` - API documentation
- `GET /api/datasets` - List all datasets
- `GET /api/datasets/{id}/info` - Dataset information  
- `POST /api/datasets/{id}/query` - Query dataset data
- `POST /api/datasets/{id}/spatial` - Spatial queries
- `GET|POST /api/search` - Search datasets

### Admin Endpoints  
- `POST /api/admin/refresh` - Refresh datasets cache

## 🚀 Quick Deployment

### Prerequisites
1. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Functions Core Tools** - [Install Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
3. **Python 3.11** - [Install Python](https://www.python.org/downloads/)

### Deploy to Azure

#### Windows:
```cmd
cd azure_function
deploy.bat
```

#### Linux/macOS:
```bash
cd azure_function
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

1. **Create Azure Resources:**
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-ethekwini-gis-mcp --location "South Africa North"

# Create storage account  
az storage account create --name stethekwinigismcp --resource-group rg-ethekwini-gis-mcp --location "South Africa North" --sku Standard_LRS

# Create Function App
az functionapp create --name func-ethekwini-gis-mcp --resource-group rg-ethekwini-gis-mcp --storage-account stethekwinigismcp --consumption-plan-location "South Africa North" --runtime python --runtime-version 3.11 --functions-version 4 --os-type Linux
```

2. **Deploy Function Code:**
```bash
cd azure_function
func azure functionapp publish func-ethekwini-gis-mcp --python
```

## 🧪 Local Development

### Setup Local Environment
```bash
cd azure_function

# Install dependencies
pip install -r requirements.txt

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Start local development server
func start
```

### Test Locally
```bash
# Health check
curl http://localhost:7071/api/health

# List datasets
curl http://localhost:7071/api/datasets

# Search datasets
curl "http://localhost:7071/api/search?q=transport"

# Query dataset
curl -X POST http://localhost:7071/api/datasets/11/query \
  -H "Content-Type: application/json" \
  -d '{"where": "STATUS=1", "max_records": 5}'
```

## 🤖 Azure AI Foundry Integration

### 1. Create AI Foundry Project
1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Create new project
3. Add your deployed Function App as a custom skill

### 2. Configure Agent
```json
{
  "name": "eThekwini GIS Assistant",
  "description": "AI agent with access to eThekwini municipal GIS data",
  "skills": [
    {
      "type": "custom",
      "name": "ethekwini_gis",
      "endpoint": "https://func-ethekwini-gis-mcp.azurewebsites.net/api",
      "authentication": {
        "type": "function_key",
        "key": "YOUR_FUNCTION_KEY"
      }
    }
  ]
}
```

### 3. Example Agent Prompts
- "Show me all transport-related datasets in eThekwini"
- "Find roads near coordinates -29.8587, 31.0218"  
- "Get statistics for the municipal boundaries dataset"
- "Search for datasets containing 'water' in their description"

## 🔐 Security Configuration

### Get Function Key
```bash
az functionapp keys list --name func-ethekwini-gis-mcp --resource-group rg-ethekwini-gis-mcp
```

### Configure CORS (if needed)
```bash
az functionapp cors add --name func-ethekwini-gis-mcp --resource-group rg-ethekwini-gis-mcp --allowed-origins https://your-domain.com
```

### Environment Variables
Configure these in Azure Portal or via CLI:
- `ETHEKWINI_REFRESH_INTERVAL` - Dataset cache refresh interval (default: 900 seconds)
- `ETHEKWINI_MAX_RECORDS` - Maximum records per query (default: 100)
- `ETHEKWINI_TIMEOUT` - HTTP timeout for API calls (default: 60 seconds)

## 📊 Monitoring & Logging

### Application Insights
The deployment automatically creates Application Insights for monitoring:
- Request/response times
- Error rates and exceptions
- Custom telemetry
- Performance metrics

### View Logs
```bash
# Stream live logs
az webapp log tail --name func-ethekwini-gis-mcp --resource-group rg-ethekwini-gis-mcp

# Download logs  
az webapp log download --name func-ethekwini-gis-mcp --resource-group rg-ethekwini-gis-mcp
```

## 🔧 Troubleshooting

### Common Issues

**1. Cold Start Performance**
- First request after idle period may be slower
- Consider using Premium plan for production

**2. Memory Limits**
- Consumption plan has 1.5GB limit
- Large datasets may hit memory limits
- Consider implementing pagination

**3. Timeout Issues**  
- Default timeout is 5 minutes
- Adjust `functionTimeout` in host.json if needed

**4. CORS Errors**
- Configure CORS for your domain
- Check browser dev tools for specific errors

### Performance Optimization
1. **Enable Dataset Caching** - Reduces API calls to eThekwini services
2. **Use Application Insights** - Monitor performance bottlenecks  
3. **Implement Pagination** - For large result sets
4. **Consider Premium Plan** - For consistent performance

## 🔄 CI/CD Pipeline

The function integrates with the main project's GitHub Actions:
- Automatic deployment on push to main
- Integration testing
- Performance monitoring

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/bonnie-mapipa/esri_gis_mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bonnie-mapipa/esri_gis_mcp/discussions)
- **Email**: bongiwemapipa82@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.