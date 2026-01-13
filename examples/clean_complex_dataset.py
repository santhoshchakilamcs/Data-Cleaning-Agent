"""Clean the complex 208-row sales dataset using LangGraph Auto-Janitor"""

import sys
sys.path.insert(0, '/Users/santhosh/auto-janitor')

from auto_janitor.langgraph_agent import LangGraphJanitor
from auto_janitor.config import Config
import pandas as pd

def main():
    """Clean complex sales dataset with semantic understanding"""
    
    # Validate configuration
    Config.validate()
    
    # Initialize the LangGraph agent
    print("="*80)
    print("LANGGRAPH AUTO-JANITOR - COMPLEX DATASET TEST")
    print("="*80)
    print("\nDataset: E-Commerce Transaction Data")
    print("Rows: 208 (200 original + 8 from duplicates)")
    print("Columns: 19")
    print("Issues: 17 different types of data quality problems")
    print("\n" + "="*80)
    
    agent = LangGraphJanitor()
    
    # Define paths
    input_csv = Config.DATA_INPUT_DIR / "complex_sales_data.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_complex_sales.csv"
    
    print(f"\nInput:  {input_csv}")
    print(f"Output: {output_csv}")
    
    # Load original to show sample issues
    print("\n" + "="*80)
    print("SAMPLE DATA QUALITY ISSUES")
    print("="*80)
    
    df_original = pd.read_csv(input_csv)
    
    print(f"\n1. Total rows: {len(df_original)}")
    print(f"2. Columns: {list(df_original.columns)}")
    
    # Show some specific issues
    print("\n3. Sample issues found:")
    
    # Negative quantities (returns)
    negative_qty = df_original[df_original['quantity'] < 0]
    if len(negative_qty) > 0:
        print(f"   - Returns/Refunds (negative qty): {len(negative_qty)} rows")
        print(f"     Example: {negative_qty.iloc[0]['transaction_id']} - qty={negative_qty.iloc[0]['quantity']}")
    
    # Missing values
    missing_email = df_original['email'].isna().sum()
    missing_phone = df_original['phone'].isna().sum()
    print(f"   - Missing emails: {missing_email} rows")
    print(f"   - Missing phones: {missing_phone} rows")
    
    # Check for price formatting issues (string in numeric column)
    price_issues = df_original[df_original['unit_price'].astype(str).str.contains('$|USD|,', na=False)]
    if len(price_issues) > 0:
        print(f"   - Price formatting issues: {len(price_issues)} rows")
        print(f"     Example: {price_issues.iloc[0]['unit_price']}")
    
    # Check for date formatting issues
    date_issues = df_original[~df_original['transaction_date'].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)]
    if len(date_issues) > 0:
        print(f"   - Date formatting issues: {len(date_issues)} rows")
        if len(date_issues) > 0:
            print(f"     Example: {date_issues.iloc[0]['transaction_date']}")
    
    print("\n" + "="*80)
    print("STARTING CLEANING PROCESS")
    print("="*80)
    
    # Clean the data with semantic understanding
    cleaned_df = agent.clean_csv(
        csv_path=str(input_csv),
        output_path=str(output_csv)
    )
    
    print("\n" + "="*80)
    print("CLEANING COMPLETE - VALIDATION")
    print("="*80)
    
    # Validate results
    print(f"\nOriginal rows: {len(df_original)}")
    print(f"Cleaned rows:  {len(cleaned_df)}")
    print(f"Rows removed:  {len(df_original) - len(cleaned_df)}")
    
    # Check if returns were preserved
    if 'quantity' in cleaned_df.columns:
        negative_qty_after = cleaned_df[cleaned_df['quantity'] < 0]
        print(f"\nReturns/Refunds preserved: {len(negative_qty_after)} rows")
        
        if len(negative_qty_after) > 0:
            print("✓ GOOD: Negative quantities were preserved!")
        elif len(negative_qty) > 0:
            print("✗ BAD: Negative quantities were converted to positive!")
    
    # Check if transaction_type column was added
    if 'transaction_type' in cleaned_df.columns:
        print("\n✓ GOOD: 'transaction_type' column added")
        print(f"  - Sales: {(cleaned_df['transaction_type'] == 'sale').sum()}")
        print(f"  - Returns: {(cleaned_df['transaction_type'] == 'return').sum()}")
    
    # Show sample of cleaned data
    print("\n" + "="*80)
    print("SAMPLE CLEANED DATA (first 5 rows)")
    print("="*80)
    print(cleaned_df.head().to_string())
    
    print("\n" + "="*80)
    print(f"✓ Cleaned data saved to: {output_csv}")
    print("="*80)


if __name__ == "__main__":
    main()

