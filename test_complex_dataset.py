"""Test LangGraph agent on complex 208-row dataset"""

import sys
sys.path.insert(0, '/Users/santhosh/auto-janitor')

from auto_janitor.langgraph_agent import LangGraphJanitor
from auto_janitor.config import Config
from unittest.mock import patch

def main():
    """Run LangGraph agent on complex dataset with auto-approval"""
    
    Config.validate()
    
    print("="*80)
    print("TESTING LANGGRAPH AGENT ON COMPLEX DATASET")
    print("="*80)
    
    agent = LangGraphJanitor()
    
    input_csv = Config.DATA_INPUT_DIR / "complex_sales_data.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_complex_sales.csv"
    
    print(f"Input:  {input_csv}")
    print(f"Output: {output_csv}\n")
    
    # Mock user input to auto-approve all confirmations
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
            
            # Check if negative quantities were preserved
            if 'quantity' in cleaned_df.columns:
                negative_qty = cleaned_df[cleaned_df['quantity'] < 0]
                print(f"\nNegative quantities (returns): {len(negative_qty)}")
                if len(negative_qty) > 0:
                    print("✓ Negative quantities PRESERVED!")
                else:
                    print("✗ Negative quantities were converted!")
            
            # Check if transaction_type was added
            if 'transaction_type' in cleaned_df.columns:
                print(f"\n✓ transaction_type column added")
                print(f"  Sales: {(cleaned_df['transaction_type'] == 'sale').sum()}")
                print(f"  Returns: {(cleaned_df['transaction_type'] == 'return').sum()}")
            
            print("\nFirst 10 rows:")
            print(cleaned_df.head(10).to_string())
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

