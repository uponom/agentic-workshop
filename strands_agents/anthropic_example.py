"""
Anthropic Claude Example (No AWS Required)
==========================================

This example uses Anthropic Claude directly, bypassing AWS Bedrock.
You'll need an Anthropic API key from https://console.anthropic.com/

Setup:
1. pip install 'strands-agents[anthropic]' strands-agents-tools
2. Get API key from https://console.anthropic.com/
3. Set environment variable: $env:ANTHROPIC_API_KEY="your_key"
"""

import os
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from strands_tools import calculator

@tool
def simple_greeting(name: str) -> str:
    """Greet someone by name.
    
    Args:
        name: The person's name to greet
        
    Returns:
        A friendly greeting message
    """
    return f"Hello {name}! Nice to meet you!"

def main():
    """Run the Anthropic example."""
    
    # Check if API key is set
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it with: $env:ANTHROPIC_API_KEY='your_key_here'")
        print("Get your key from: https://console.anthropic.com/")
        return
    
    print("🤖 Anthropic Claude Agent Example")
    print("=" * 40)
    
    # Create Anthropic model
    model = AnthropicModel(
        client_args={"api_key": api_key},
        model_id="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        params={"temperature": 0.7}
    )
    
    # Create agent
    agent = Agent(
        model=model,
        tools=[calculator, simple_greeting],
        system_prompt="You are a helpful assistant with calculation and greeting capabilities."
    )
    
    # Test the agent
    print("\n🔢 Testing calculator...")
    response = agent("What's 42 * 17?")
    print(f"Agent: {response}")
    
    print("\n👋 Testing greeting...")
    response = agent("Please greet me, my name is Sam")
    print(f"Agent: {response}")
    
    print("\n✅ Anthropic example completed!")

if __name__ == "__main__":
    main()