#!/usr/bin/env python3
"""
Demo script for CDK Agent - shows a few quick interactions
"""

from cdk_agent import CDKAgent, check_prerequisites

def demo_cdk_agent():
    """Demo the CDK agent with a few sample questions."""
    print("🚀 CDK Agent Demo")
    print("=" * 50)
    
    if not check_prerequisites():
        print("❌ Prerequisites not met")
        return
    
    # Initialize agent
    print("\n🤖 Initializing CDK Agent...")
    cdk_agent = CDKAgent()
    
    if not cdk_agent.initialize():
        print("❌ Failed to initialize agent")
        return
    
    # Demo questions
    questions = [
        "How do I create a new CDK project for Python?",
        "What are CDK constructs and how do I use them?",
        "Show me how to create a Lambda function with CDK"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Demo Question {i}: {question}")
        print("🤔 CDK Agent thinking...")
        
        response = cdk_agent.chat(question)
        
        # Show first 300 characters of response
        if len(response) > 300:
            display = response[:300] + "...\n[Response truncated for demo]"
        else:
            display = response
        
        print(f"💬 CDK Agent: {display}")
        print("-" * 50)
    
    print("\n✅ Demo completed! The CDK Agent is ready for use.")
    print("Run 'python cdk_agent.py --interactive' for full interaction.")

if __name__ == "__main__":
    demo_cdk_agent()