"""Quick test to verify Auto-Janitor setup"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError:
        print("✗ pandas - run: poetry install")
        return False
    
    try:
        import polars
        print("✓ polars")
    except ImportError:
        print("✗ polars - run: poetry install")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError:
        print("✗ python-dotenv - run: poetry install")
        return False
    
    try:
        from rich.console import Console
        print("✓ rich")
    except ImportError:
        print("✗ rich - run: poetry install")
        return False
    
    return True


def test_structure():
    """Test that project structure is correct"""
    print("\nTesting project structure...")
    
    required_files = [
        "auto_janitor/__init__.py",
        "auto_janitor/agent.py",
        "auto_janitor/config.py",
        "auto_janitor/llm.py",
        "auto_janitor/sandbox.py",
        "data/input/messy_sales.csv",
        "examples/basic_usage.py",
        ".env.example",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - missing!")
            all_exist = False
    
    return all_exist


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found - copy .env.example to .env and add your API keys")
        return False
    
    try:
        from auto_janitor.config import Config
        
        if Config.LLM_PROVIDER == "openai" and not Config.OPENAI_API_KEY:
            print("✗ OPENAI_API_KEY not set in .env")
            return False
        elif Config.LLM_PROVIDER == "anthropic" and not Config.ANTHROPIC_API_KEY:
            print("✗ ANTHROPIC_API_KEY not set in .env")
            return False
        
        print(f"✓ LLM Provider: {Config.LLM_PROVIDER}")
        print(f"✓ Model: {Config.MODEL_NAME}")
        print(f"✓ Max Iterations: {Config.MAX_ITERATIONS}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("AUTO-JANITOR SETUP TEST")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Structure", test_structure()))
    results.append(("Configuration", test_config()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to use Auto-Janitor.")
        print("\nRun: poetry run python examples/basic_usage.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

