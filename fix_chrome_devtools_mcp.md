# Fix Chrome DevTools MCP Server Issue

## Problem
The chrome-devtools MCP server is failing because `npx` is not available on your Windows system. The error shows:
```
'npx' is not recognized as an internal or external command
```

## Root Cause
The chrome-devtools MCP server requires Node.js and npm to be installed, but they're missing from your system.

## Solutions

### Solution 1: Install Node.js (Recommended)

1. **Download Node.js**:
   - Go to https://nodejs.org/
   - Download the LTS version for Windows
   - Run the installer and follow the setup wizard

2. **Verify Installation**:
   ```powershell
   node --version
   npm --version
   npx --version
   ```

3. **Restart Kiro** after installation to pick up the new PATH

### Solution 2: Disable Chrome DevTools MCP Server

If you don't need the chrome-devtools functionality, you can disable it:

1. **Edit MCP Configuration**:
   ```powershell
   notepad "C:\Users\yurap\.kiro\settings\mcp.json"
   ```

2. **Add "disabled": true** to the chrome-devtools section:
   ```json
   "chrome-devtools": {
     "command": "npx",
     "args": ["-y", "chrome-devtools-mcp@latest"],
     "disabled": true
   }
   ```

### Solution 3: Alternative Chrome DevTools Server

If you want to keep chrome-devtools functionality but avoid Node.js, you could try using uvx instead (though this may not work for all Node.js packages):

```json
"chrome-devtools": {
  "command": "uvx",
  "args": ["chrome-devtools-mcp@latest"],
  "disabled": false
}
```

## Quick Fix Commands

### Option A: Disable Chrome DevTools MCP
```powershell
# Backup current config
copy "C:\Users\yurap\.kiro\settings\mcp.json" "C:\Users\yurap\.kiro\settings\mcp.json.backup"

# Edit the config to disable chrome-devtools
# (You'll need to manually edit the file to add "disabled": true)
```

### Option B: Install Node.js via Chocolatey (if you have it)
```powershell
choco install nodejs
```

### Option C: Install Node.js via Winget (Windows 10/11)
```powershell
winget install OpenJS.NodeJS
```

## Verification

After applying any solution, restart Kiro and check the MCP logs. You should no longer see the npx error.

## What Chrome DevTools MCP Provides

The chrome-devtools MCP server typically provides:
- Browser automation capabilities
- Web scraping tools
- DOM manipulation
- Screenshot capture
- Performance monitoring

If you don't need these features, disabling it is the simplest solution.