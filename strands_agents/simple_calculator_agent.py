"""
Simple Calculator Agent Example
==============================

A minimal example showing how to create an agent with basic tools.
This example works with any provider (Bedrock, Anthropic, OpenAI, etc.)
"""

from strands import Agent, tool
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
    """Run the simple calculator agent example."""
    
    print("🧮 Simple Calculator Agent")
    print("=" * 30)
    
    # Create agent with minimal configuration
    # Uses Bedrock Claude 4 Sonnet by default
    agent = Agent(
        tools=[calculator, simple_greeting],
        system_prompt="You are a friendly calculator assistant. Help users with math and greet them warmly."
    )
    
    # Test basic functionality
    print("\n🔢 Testing calculator...")
    response = agent("What's 25 * 17 + 100?")
    print(f"Agent: {response}")
    
    print("\n👋 Testing greeting...")
    response = agent("Please greet me, my name is Alex")
    print(f"Agent: {response}")
    
    print("\n💭 Testing conversation memory...")
    response = agent("What's my name again?")
    print(f"Agent: {response}")
    
    print("\n✅ Simple example completed!")

if __name__ == "__main__":
    main()