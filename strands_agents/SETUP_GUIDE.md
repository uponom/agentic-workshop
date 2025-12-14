# Strands Agents Setup Guide

## Quick Setup for Amazon Bedrock (Recommended)

### Option 1: Bedrock API Key (Easiest for Development)

1. **Get a Bedrock API Key:**
   - Open [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
   - Navigate to "API keys" in the left sidebar
   - Click "Generate long-term API key"
   - Set expiration (30 days max for development)
   - Copy the key (shown only once!)

2. **Enable Model Access:**
   - In Bedrock Console → "Model access" → "Manage model access"
   - Enable "Claude 4 Sonnet" or your preferred model
   - Wait a few minutes for access to propagate

3. **Set Environment Variable:**
   ```powershell
   # Windows PowerShell
   $env:AWS_BEDROCK_API_KEY="your_bedrock_api_key_here"
   
   # Or add to your system environment variables permanently
   ```

4. **Test the Setup:**
   ```powershell
   python strands_agents/getting_started_example.py
   ```

### Option 2: AWS Credentials (Production)

1. **Install AWS CLI:**
   ```powershell
   # If not already installed
   pip install awscli
   ```

2. **Configure AWS Credentials:**
   ```powershell
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key  
   # Enter your default region (e.g., us-west-2)
   # Enter output format (json)
   ```

3. **Enable Model Access:** (Same as Option 1, step 2)

4. **Test the Setup:** (Same as Option 1, step 4)

## Alternative Providers

### Anthropic Claude (Direct)

1. **Get API Key:** [Anthropic Console](https://console.anthropic.com/)
2. **Install Extension:** `pip install 'strands-agents[anthropic]'`
3. **Set Environment:** `$env:ANTHROPIC_API_KEY="your_key"`

### OpenAI GPT

1. **Get API Key:** [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Install Extension:** `pip install 'strands-agents[openai]'`
3. **Set Environment:** `$env:OPENAI_API_KEY="your_key"`

### Google Gemini

1. **Get API Key:** [Google AI Studio](https://aistudio.google.com/apikey)
2. **Install Extension:** `pip install 'strands-agents[gemini]'`
3. **Set Environment:** `$env:GOOGLE_API_KEY="your_key"`

## Troubleshooting

### "Access denied to model"
- Enable model access in Bedrock Console
- Wait a few minutes for propagation
- Check your region matches the model availability

### "Invalid API key"
- Verify the environment variable is set: `echo $env:AWS_BEDROCK_API_KEY`
- Check for typos in the key
- Regenerate key if expired (30-day limit)

### "Module not found"
- Install provider extension: `pip install 'strands-agents[provider]'`
- Restart Python interpreter

## Next Steps

1. Run the getting started example
2. Explore the existing examples in this folder
3. Create your own custom tools
4. Build domain-specific agents

## Resources

- [Strands Documentation](https://docs.strands.ai/)
- [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
- [Community Tools](https://github.com/strands-ai/strands-agents-tools)