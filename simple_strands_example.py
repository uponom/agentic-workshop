#!/usr/bin/env python3
"""
Simple Strands Agent Example
Demonstrates basic agent creation with tools and conversation memory.
"""

from strands import Agent, tool
from strands_tools import calculator, http_request

def main():
    print("🚀 Creating a Strands Agent with tools...")
    
    # Create a custom tool
    @tool
    def get_weather_info(city: str) -> str:
        """Get weather information for a city.
        
        Args:
            city: The name of the city to get weather for
        """
        return f"Weather in {city}: Sunny, 72°F (simulated data)"
    
    # Create an agent with tools (uses Bedrock Claude 4 Sonnet by default)
    agent = Agent(
        tools=[calculator, http_request, get_weather_info],
        system_prompt="You are a helpful assistant with access to calculation, web requests, and weather tools. Be concise and helpful."
    )
    
    print("✅ Agent created successfully!")
    print("\n" + "="*50)
    print("Testing the agent with a simple calculation...")
    print("="*50)
    
    # Test 1: Simple calculation
    response = agent("What is 15 * 23 + 47?")
    print(f"🤖 Agent: {response}")
    
    print("\n" + "="*50)
    print("Testing conversation memory...")
    print("="*50)
    
    # Test 2: Conversation memory
    agent("My favorite number is 42")
    response = agent("What's my favorite number multiplied by 3?")
    print(f"🤖 Agent: {response}")
    
    print("\n" + "="*50)
    print("Testing custom tool...")
    print("="*50)
    
    # Test 3: Custom tool
    response = agent("What's the weather like in Seattle?")
    print(f"🤖 Agent: {response}")
    
    print("\n✨ Demo complete! The agent successfully used tools and maintained conversation context.")

if __name__ == "__main__":
    main()