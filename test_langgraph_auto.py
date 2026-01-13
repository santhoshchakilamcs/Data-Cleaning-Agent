"""Test LangGraph agent with auto-approval for testing"""

import sys
sys.path.insert(0, '/Users/santhosh/auto-janitor')

from auto_janitor.langgraph_agent import LangGraphJanitor
from auto_janitor.config import Config
from unittest.mock import patch

def main():
    """Run LangGraph test with auto-approval"""
    
    Config.validate()
    
    print("="*80)
    print("LANGGRAPH AUTO-JANITOR TEST")
    print("="*80)
    
    agent = LangGraphJanitor()
    
    input_csv = Config.DATA_INPUT_DIR / "messy_sales.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_sales_langgraph_test.csv"
    
    # Mock user input to auto-approve
    with patch('builtins.input', return_value='yes'):
        try:
            cleaned_df = agent.clean_csv(
                csv_path=str(input_csv),
                output_path=str(output_csv)
            )
            
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80)
            print(f"Final shape: {cleaned_df.shape}")
            print("\nFirst 10 rows:")
            print(cleaned_df.head(10).to_string())
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

