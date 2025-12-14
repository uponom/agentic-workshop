# PowerShell script to set Bedrock API key
# Replace 'your_bedrock_api_key_here' with your actual API key

# Set for current session
$env:AWS_BEDROCK_API_KEY="your_bedrock_api_key_here"

# Verify it's set
Write-Host "AWS_BEDROCK_API_KEY is set to: $env:AWS_BEDROCK_API_KEY"

# To make it permanent, add to your PowerShell profile or system environment variables
Write-Host "To make this permanent, run:"
Write-Host '[Environment]::SetEnvironmentVariable("AWS_BEDROCK_API_KEY", "your_key_here", "User")'