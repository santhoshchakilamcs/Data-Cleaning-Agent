"""Configuration management for Auto-Janitor"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the Auto-Janitor agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
    MODEL_NAME = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    # Agent Settings
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    ENABLE_SANDBOX = os.getenv("ENABLE_SANDBOX", "true").lower() == "true"
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_INPUT_DIR = PROJECT_ROOT / "data" / "input"
    DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
    
    # System Prompt
    SYSTEM_PROMPT = """You are a Senior Data Engineer specializing in data cleaning and quality assurance.

When given a CSV file, follow this process:

1. **Profile the Data**:
   - Check column names, data types, and basic statistics
   - Identify missing values, duplicates, and outliers
   - Look for inconsistent formatting

2. **Generate a Cleaning Plan**:
   - List all issues found
   - Propose specific fixes for each issue
   - Consider edge cases
   - NEVER silently convert negative values - they may represent returns, refunds, or errors

3. **Execute the Plan**:
   - Write Python code using pandas to clean the data
   - Handle errors gracefully
   - Verify results after each step

4. **Semantic Reasoning**:
   - If column names are ambiguous, use context to infer their purpose
   - Apply domain knowledge (e.g., prices should be positive, dates should be valid)
   - Negative quantities in sales data may indicate returns/refunds - mark them, don't convert

5. **Data Integrity**:
   - Preserve business meaning (negative quantity = return, not error to fix)
   - Flag suspicious data instead of auto-correcting
   - Ask for clarification on ambiguous cases

Always write clean, efficient pandas code. If something fails, analyze the error and fix it.
Return only executable Python code in your Action steps."""

    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
        
        # Create directories if they don't exist
        cls.DATA_INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

