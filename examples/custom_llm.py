"""Example using a custom LLM provider"""

from auto_janitor import AutoJanitor
from auto_janitor.llm import get_llm, LLMProvider
from auto_janitor.config import Config

def main():
    """Run Auto-Janitor with a specific LLM"""
    
    Config.validate()
    
    # Option 1: Use OpenAI GPT-4o
    # llm = get_llm(provider=LLMProvider.OPENAI, model="gpt-4o")
    
    # Option 2: Use Anthropic Claude (default)
    llm = get_llm(provider=LLMProvider.ANTHROPIC, model="claude-3-5-sonnet-20241022")
    
    # Initialize agent with custom LLM
    agent = AutoJanitor(llm=llm, max_iterations=15)
    
    # Clean data
    input_csv = Config.DATA_INPUT_DIR / "messy_sales.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_sales_custom.csv"
    
    cleaned_df = agent.clean_csv(
        csv_path=str(input_csv),
        output_path=str(output_csv)
    )
    
    print(f"\nCleaned {len(cleaned_df)} rows successfully!")


if __name__ == "__main__":
    main()

