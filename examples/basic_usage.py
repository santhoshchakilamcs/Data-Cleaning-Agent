"""Basic usage example for Auto-Janitor"""

from pathlib import Path
from auto_janitor import AutoJanitor
from auto_janitor.config import Config

def main():
    """Run a basic data cleaning example"""
    
    # Validate configuration
    Config.validate()
    
    # Initialize the agent
    agent = AutoJanitor()
    
    # Define paths
    input_csv = Config.DATA_INPUT_DIR / "messy_sales.csv"
    output_csv = Config.DATA_OUTPUT_DIR / "cleaned_sales.csv"
    
    # Clean the data
    print("Starting Auto-Janitor...")
    print(f"Input: {input_csv}")
    print(f"Output: {output_csv}\n")
    
    cleaned_df = agent.clean_csv(
        csv_path=str(input_csv),
        output_path=str(output_csv)
    )
    
    print("\n" + "="*80)
    print("FINAL CLEANED DATA")
    print("="*80)
    print(cleaned_df.to_string())
    print("\n" + "="*80)
    print(f"Cleaned data shape: {cleaned_df.shape}")
    print("="*80)


if __name__ == "__main__":
    main()

