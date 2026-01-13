"""Example using LangGraph-based Auto-Janitor with semantic understanding"""

import sys
sys.path.insert(0, '/Users/santhosh/auto-janitor')

from auto_janitor.langgraph_agent import LangGraphJanitor
from auto_janitor.config import Config

def main():
    """Run LangGraph-based data cleaning"""
    
    # Validate configuration
    Config.validate()
    
    # Initialize the LangGraph agent
    print("Initializing LangGraph Auto-Janitor...")
    agent = LangGraphJanitor()
    
    # Define paths
    input_csv = Config.DATA_INPUT_DIR / "messy_sales.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_sales_langgraph.csv"
    
    print(f"Input: {input_csv}")
    print(f"Output: {output_csv}\n")
    
    # Clean the data with semantic understanding
    cleaned_df = agent.clean_csv(
        csv_path=str(input_csv),
        output_path=str(output_csv)
    )
    
    print("\n" + "="*80)
    print("FINAL CLEANED DATA")
    print("="*80)
    print(cleaned_df.to_string())
    print("\n" + "="*80)
    print(f"Final shape: {cleaned_df.shape}")
    print("="*80)


if __name__ == "__main__":
    main()

