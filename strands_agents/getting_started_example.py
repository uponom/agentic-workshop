"""
Getting Started with Strands Agents SDK
=======================================

This example demonstrates the basic usage of Strands agents with:
1. Custom tools
2. Community tools
3. Conversation memory
4. Amazon Bedrock (default provider)

Before running this example, make sure you have:
1. AWS credentials configured (see setup instructions below)
2. Bedrock model access enabled in AWS console
"""

from strands import Agent, tool
from strands_tools import calculator, python_repl, http_request

# Define a custom tool
@tool
def get_current_time() -> str:
    """Get the current date and time.
    
    Returns:
        Current date and time as a string
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def word_count(text: str) -> int:
    """Count the number of words in a text.
    
    Args:
        text: The text to count words in
        
    Returns:
        Number of words in the text
    """
    return len(text.split())

def main():
    """Main function to demonstrate agent usage."""
    
    # Create an agent with custom and community tools
    # Uses Bedrock Claude 4 Sonnet by default
    agent = Agent(
        tools=[get_current_time, word_count, calculator, python_repl, http_request],
        system_prompt="""You are a helpful assistant with access to various tools. 
        You can:
        - Get the current time
        - Count words in text
        - Perform calculations
        - Execute Python code
        - Make HTTP requests
        
        Always be helpful and explain what you're doing when using tools."""
    )
    
    print("🤖 Strands Agent Ready!")
    print("=" * 50)
    
    # Example 1: Simple question
    print("\n📝 Example 1: Basic interaction")
    response = agent("What's the current time?")
    print(f"Agent: {response}")
    
    # Example 2: Using multiple tools
    print("\n🔢 Example 2: Using multiple tools")
    response = agent("Calculate 15 * 23, then tell me how many words are in your response")
    print(f"Agent: {response}")
    
    # Example 3: Conversation memory
    print("\n💭 Example 3: Conversation memory")
    agent("My name is Alice and I'm learning about AI agents")
    response = agent("What's my name and what am I learning about?")
    print(f"Agent: {response}")
    
    # Example 4: Python code execution
    print("\n🐍 Example 4: Python code execution")
    response = agent("Write and run Python code to create a list of the first 10 fibonacci numbers")
    print(f"Agent: {response}")
    
    print("\n✅ All examples completed!")

if __name__ == "__main__":
    main()