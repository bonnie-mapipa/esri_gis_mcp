@echo off
REM Azure Function Deployment Script for eThekwini GIS MCP (Windows)
REM This script deploys the MCP as an Azure Function App

setlocal enabledelayedexpansion

REM Configuration
set RESOURCE_GROUP=rg-ethekwini-gis-mcp
set FUNCTION_APP_NAME=func-ethekwini-gis-mcp
set STORAGE_ACCOUNT=stethekwinigismcp
set LOCATION="South Africa North"
set RUNTIME=python
set RUNTIME_VERSION=3.11

echo 🚀 Deploying eThekwini GIS MCP to Azure Functions...

REM Check if Azure CLI is installed
where az >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Azure CLI not found. Please install Azure CLI first.
    exit /b 1
)

REM Login to Azure (if not already logged in)
echo 🔐 Checking Azure login status...
az account show >nul 2>&1
if %errorlevel% neq 0 (
    echo Please log in to Azure:
    az login
)

REM Create resource group
echo 📁 Creating resource group...
az group create --name %RESOURCE_GROUP% --location %LOCATION% --tags project=ethekwini-gis-mcp environment=production

REM Create storage account
echo 💾 Creating storage account...
az storage account create --name %STORAGE_ACCOUNT% --resource-group %RESOURCE_GROUP% --location %LOCATION% --sku Standard_LRS --kind StorageV2

REM Create Function App
echo ⚡ Creating Function App...
az functionapp create --name %FUNCTION_APP_NAME% --resource-group %RESOURCE_GROUP% --storage-account %STORAGE_ACCOUNT% --consumption-plan-location %LOCATION% --runtime %RUNTIME% --runtime-version %RUNTIME_VERSION% --functions-version 4 --os-type Linux

REM Configure app settings
echo ⚙️ Configuring application settings...
az functionapp config appsettings set --name %FUNCTION_APP_NAME% --resource-group %RESOURCE_GROUP% --settings ETHEKWINI_REFRESH_INTERVAL=900 ETHEKWINI_MAX_RECORDS=100 ETHEKWINI_TIMEOUT=60 WEBSITE_RUN_FROM_PACKAGE=1

REM Enable Application Insights
echo 📊 Enabling Application Insights...
az monitor app-insights component create --app %FUNCTION_APP_NAME% --location %LOCATION% --resource-group %RESOURCE_GROUP% --kind web

REM Deploy the function
echo 📦 Deploying function code...
cd /d "%~dp0"
func azure functionapp publish %FUNCTION_APP_NAME% --python

echo ✅ Deployment completed successfully!
echo.
echo 📍 Function App URL: https://%FUNCTION_APP_NAME%.azurewebsites.net
echo 📍 API Documentation: https://%FUNCTION_APP_NAME%.azurewebsites.net/api
echo 📍 Health Check: https://%FUNCTION_APP_NAME%.azurewebsites.net/api/health
echo.
echo 🔗 To use with Azure AI Foundry agents, configure the base URL as:
echo    https://%FUNCTION_APP_NAME%.azurewebsites.net/api
echo.
echo 🔑 Don't forget to configure authentication and get the function key:
echo    az functionapp keys list --name %FUNCTION_APP_NAME% --resource-group %RESOURCE_GROUP%

pause