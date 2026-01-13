"""Test improved LangGraph agent with negative quantity handling"""

import sys
sys.path.insert(0, '/Users/santhosh/auto-janitor')

from auto_janitor.langgraph_agent import LangGraphJanitor
from auto_janitor.config import Config
from unittest.mock import patch

def main():
    """Test with auto-approval"""
    
    Config.validate()
    
    print("="*80)
    print("TESTING IMPROVED NEGATIVE QUANTITY HANDLING")
    print("="*80)
    
    agent = LangGraphJanitor()
    
    input_csv = Config.DATA_INPUT_DIR / "messy_sales.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_sales_improved.csv"
    
    # Mock user input to auto-approve
    with patch('builtins.input', return_value='yes'):
        try:
            cleaned_df = agent.clean_csv(
                csv_path=str(input_csv),
                output_path=str(output_csv)
            )
            
            print("\n" + "="*80)
            print("CHECKING NEGATIVE QUANTITY HANDLING")
            print("="*80)
            
            # Find the Widget C row
            widget_c = cleaned_df[cleaned_df['product_name'] == 'Widget C']
            
            if not widget_c.empty:
                print("\nWidget C row:")
                print(widget_c.to_string())
                
                quantity = widget_c.iloc[0]['quantity']
                print(f"\nQuantity value: {quantity}")
                
                if 'transaction_type' in cleaned_df.columns:
                    trans_type = widget_c.iloc[0]['transaction_type']
                    print(f"Transaction type: {trans_type}")
                    
                    if quantity < 0 or trans_type == 'return':
                        print("\n✓ CORRECT: Negative quantity preserved or marked as return!")
                    else:
                        print("\n✗ WRONG: Negative quantity was converted to positive!")
                else:
                    if quantity < 0:
                        print("\n✓ CORRECT: Negative quantity preserved!")
                    else:
                        print("\n✗ WRONG: Negative quantity was converted to positive!")
            
            print("\n" + "="*80)
            print("FULL CLEANED DATA")
            print("="*80)
            print(cleaned_df.to_string())
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

