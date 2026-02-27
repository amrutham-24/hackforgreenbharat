# Green Bharat ESG Platform - Azure Deployment Script
# Prerequisites: Azure CLI logged in, subscription set

$RG = "green-bharath-rg"
$LOCATION = "centralindia"
$APP_PLAN = "green-bharath-plan"
$API_APP = "greenbharat-api"
$WEB_APP = "greenbharat-web"
$PG_SERVER = "greenbharat-pg"
$PG_ADMIN = "esgadmin"
$PG_PASS = "EsgP@ss2026!"
$REDIS_NAME = "greenbharat-redis"

Write-Host "=== Creating Resource Group ===" -ForegroundColor Green
az group create --name $RG --location $LOCATION

Write-Host "=== Creating PostgreSQL Flexible Server ===" -ForegroundColor Green
az postgres flexible-server create `
    --resource-group $RG `
    --name $PG_SERVER `
    --location $LOCATION `
    --admin-user $PG_ADMIN `
    --admin-password $PG_PASS `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 16 `
    --yes

az postgres flexible-server db create `
    --resource-group $RG `
    --server-name $PG_SERVER `
    --database-name esg_db

az postgres flexible-server firewall-rule create `
    --resource-group $RG `
    --name $PG_SERVER `
    --rule-name AllowAzure `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

Write-Host "=== Creating Redis Cache ===" -ForegroundColor Green
az redis create `
    --resource-group $RG `
    --name $REDIS_NAME `
    --location $LOCATION `
    --sku Basic `
    --vm-size c0

Write-Host "=== Creating App Service Plan ===" -ForegroundColor Green
az appservice plan create `
    --resource-group $RG `
    --name $APP_PLAN `
    --location $LOCATION `
    --sku B1 `
    --is-linux

Write-Host "=== Creating API Web App ===" -ForegroundColor Green
az webapp create `
    --resource-group $RG `
    --plan $APP_PLAN `
    --name $API_APP `
    --runtime "PYTHON:3.12"

$PG_HOST = "$PG_SERVER.postgres.database.azure.com"
$DB_URL = "postgresql+asyncpg://${PG_ADMIN}:${PG_PASS}@${PG_HOST}:5432/esg_db?ssl=require"
$DB_URL_SYNC = "postgresql://${PG_ADMIN}:${PG_PASS}@${PG_HOST}:5432/esg_db?sslmode=require"

$REDIS_KEY = (az redis list-keys --resource-group $RG --name $REDIS_NAME --query primaryKey -o tsv)
$REDIS_URL = "rediss://:${REDIS_KEY}@${REDIS_NAME}.redis.cache.windows.net:6380/0"

az webapp config appsettings set --resource-group $RG --name $API_APP --settings `
    DATABASE_URL=$DB_URL `
    DATABASE_URL_SYNC=$DB_URL_SYNC `
    REDIS_URL=$REDIS_URL `
    JWT_SECRET_KEY="$(New-Guid)" `
    CORS_ORIGINS="https://${WEB_APP}.azurewebsites.net" `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    APP_ENV=production

Write-Host "=== Creating Frontend Web App ===" -ForegroundColor Green
az webapp create `
    --resource-group $RG `
    --plan $APP_PLAN `
    --name $WEB_APP `
    --runtime "NODE:22-lts"

az webapp config appsettings set --resource-group $RG --name $WEB_APP --settings `
    NEXT_PUBLIC_API_URL="https://${API_APP}.azurewebsites.net" `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host "API URL:      https://${API_APP}.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Frontend URL: https://${WEB_APP}.azurewebsites.net" -ForegroundColor Cyan
Write-Host "PostgreSQL:   $PG_HOST" -ForegroundColor Cyan
Write-Host "Redis:        ${REDIS_NAME}.redis.cache.windows.net" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Deploy API: az webapp deployment source config-zip --resource-group $RG --name $API_APP --src api.zip"
Write-Host "2. Deploy Web: az webapp deployment source config-zip --resource-group $RG --name $WEB_APP --src web.zip"
