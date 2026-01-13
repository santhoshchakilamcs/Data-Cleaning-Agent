"""Quick test of LangGraph agent"""

import sys
sys.path.insert(0, '/Users/santhosh/auto-janitor')

print("Testing imports...")

try:
    from auto_janitor.config import Config
    print("✓ Config imported")
except Exception as e:
    print(f"✗ Config import failed: {e}")
    sys.exit(1)

try:
    from langgraph.graph import StateGraph, END
    print("✓ LangGraph imported")
except Exception as e:
    print(f"✗ LangGraph import failed: {e}")
    sys.exit(1)

try:
    from langchain_openai import ChatOpenAI
    print("✓ LangChain OpenAI imported")
except Exception as e:
    print(f"✗ LangChain OpenAI import failed: {e}")
    sys.exit(1)

try:
    from auto_janitor.langgraph_agent import LangGraphJanitor
    print("✓ LangGraphJanitor imported")
except Exception as e:
    print(f"✗ LangGraphJanitor import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All imports successful!")
print("\nInitializing agent...")

try:
    Config.validate()
    agent = LangGraphJanitor()
    print("✓ Agent initialized successfully!")
except Exception as e:
    print(f"✗ Agent initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ Test passed!")

