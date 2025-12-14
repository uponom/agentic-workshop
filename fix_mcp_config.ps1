# PowerShell script to fix Chrome DevTools MCP configuration
# This script will disable the chrome-devtools MCP server to stop the npx errors

$mcpConfigPath = "$env:USERPROFILE\.kiro\settings\mcp.json"
$backupPath = "$env:USERPROFILE\.kiro\settings\mcp.json.backup"

Write-Host "🔧 Fixing Chrome DevTools MCP Configuration" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if config file exists
if (-not (Test-Path $mcpConfigPath)) {
    Write-Host "❌ MCP config file not found at: $mcpConfigPath" -ForegroundColor Red
    exit 1
}

# Create backup
Write-Host "📋 Creating backup..." -ForegroundColor Yellow
Copy-Item $mcpConfigPath $backupPath -Force
Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green

# Read current config
Write-Host "📖 Reading current configuration..." -ForegroundColor Yellow
$configContent = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json

# Check if chrome-devtools exists
if ($configContent.mcpServers.PSObject.Properties.Name -contains "chrome-devtools") {
    Write-Host "🔍 Found chrome-devtools server configuration" -ForegroundColor Yellow
    
    # Add disabled property
    $configContent.mcpServers."chrome-devtools" | Add-Member -NotePropertyName "disabled" -NotePropertyValue $true -Force
    
    Write-Host "🚫 Disabling chrome-devtools MCP server..." -ForegroundColor Yellow
    
    # Write back to file
    $configContent | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath -Encoding UTF8
    
    Write-Host "✅ Chrome DevTools MCP server has been disabled" -ForegroundColor Green
    Write-Host "🔄 Please restart Kiro to apply changes" -ForegroundColor Cyan
} 
else {
    Write-Host "ℹ️  Chrome DevTools server not found in configuration" -ForegroundColor Blue
}

Write-Host "`n📊 Current MCP Server Status:" -ForegroundColor Cyan
$configContent.mcpServers.PSObject.Properties | ForEach-Object {
    $serverName = $_.Name
    $serverConfig = $_.Value
    $status = if ($serverConfig.disabled -eq $true) { "❌ Disabled" } else { "✅ Enabled" }
    Write-Host "  $serverName : $status" -ForegroundColor White
}

Write-Host "`n🎉 Configuration update complete!" -ForegroundColor Green
Write-Host "To re-enable chrome-devtools later, either:" -ForegroundColor Yellow
Write-Host "1. Install Node.js from https://nodejs.org/" -ForegroundColor Yellow
Write-Host "2. Edit the config file and set 'disabled': false" -ForegroundColor Yellow