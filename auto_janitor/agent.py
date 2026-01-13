"""Core Auto-Janitor Agent with ReAct Loop"""

import re
from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from auto_janitor.config import Config
from auto_janitor.llm import get_llm, BaseLLM
from auto_janitor.sandbox import PythonSandbox


console = Console()


class AutoJanitor:
    """Autonomous data cleaning agent using ReAct loop"""
    
    def __init__(self, llm: Optional[BaseLLM] = None, max_iterations: int = None):
        """
        Initialize the Auto-Janitor agent
        
        Args:
            llm: LLM provider instance (defaults to config settings)
            max_iterations: Maximum ReAct loop iterations (defaults to config)
        """
        self.llm = llm or get_llm()
        self.max_iterations = max_iterations or Config.MAX_ITERATIONS
        self.conversation_history: List[Dict[str, str]] = []
        self.sandbox: Optional[PythonSandbox] = None
        
    def clean_csv(self, csv_path: str, output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Clean a CSV file using the ReAct loop
        
        Args:
            csv_path: Path to input CSV file
            output_path: Optional path to save cleaned CSV
            
        Returns:
            Cleaned DataFrame
        """
        # Load the CSV
        console.print(f"\n[bold blue]Loading CSV:[/bold blue] {csv_path}")
        df = pd.read_csv(csv_path)
        console.print(f"[green]✓[/green] Loaded {len(df)} rows, {len(df.columns)} columns\n")
        
        # Initialize sandbox
        self.sandbox = PythonSandbox(df)
        
        # Get initial data profile
        profile = self._profile_dataframe(df)
        
        # Initialize conversation
        self.conversation_history = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": f"""I need you to clean this CSV file.

Here's the data profile:
{profile}

First few rows:
{df.head(10).to_string()}

Please analyze the data and create a cleaning plan. Then execute it step by step using the ReAct framework:
- Thought: Explain what you're going to do
- Action: Write Python code to execute (use the variable 'df' for the dataframe)
- Observation: I'll run the code and show you the result

After each observation, continue with the next thought-action pair until the data is clean.
When you're done, say "CLEANING_COMPLETE" in your thought."""}
        ]
        
        # Run ReAct loop
        cleaned_df = self._react_loop()
        
        # Save if output path provided
        if output_path:
            cleaned_df.to_csv(output_path, index=False)
            console.print(f"\n[bold green]✓ Saved cleaned data to:[/bold green] {output_path}")
        
        return cleaned_df

    def _react_loop(self) -> pd.DataFrame:
        """Execute the ReAct (Reasoning + Action) loop"""
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
            console.print(f"[bold cyan]Iteration {iteration}/{self.max_iterations}[/bold cyan]")
            console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")

            # Get LLM response
            response = self.llm.generate(self.conversation_history)
            self.conversation_history.append({"role": "assistant", "content": response})

            # Display the response
            console.print(Panel(response, title="[bold yellow]Agent Response[/bold yellow]", border_style="yellow"))

            # Check if cleaning is complete
            if "CLEANING_COMPLETE" in response:
                console.print("\n[bold green]✓ Cleaning completed successfully![/bold green]")
                break

            # Extract and execute code
            code_blocks = self._extract_code_blocks(response)

            if code_blocks:
                for code in code_blocks:
                    console.print("\n[bold magenta]Executing Code:[/bold magenta]")
                    console.print(Syntax(code, "python", theme="monokai", line_numbers=True))

                    # Execute in sandbox
                    success, output, result_df = self.sandbox.execute(code)

                    if success:
                        console.print(f"\n[green]✓ Success:[/green] {output}")
                        self.sandbox.update_dataframe(result_df)
                    else:
                        console.print(f"\n[red]✗ Error:[/red]\n{output}")

                    # Add observation to conversation
                    observation = f"Observation: {output}"
                    self.conversation_history.append({"role": "user", "content": observation})
            else:
                # No code found, prompt for action
                self.conversation_history.append({
                    "role": "user",
                    "content": "Please provide the Python code to execute in your next Action."
                })

        if iteration >= self.max_iterations:
            console.print("\n[bold yellow]⚠ Reached maximum iterations[/bold yellow]")

        return self.sandbox.get_dataframe()

    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract Python code blocks from LLM response"""
        # Look for code blocks marked with ```python or ```
        pattern = r'```(?:python)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [match.strip() for match in matches if match.strip()]

    def _profile_dataframe(self, df: pd.DataFrame) -> str:
        """Generate a profile of the dataframe"""
        profile_parts = []

        profile_parts.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        profile_parts.append(f"\nColumns: {', '.join(df.columns.tolist())}")

        profile_parts.append("\nData Types:")
        for col, dtype in df.dtypes.items():
            profile_parts.append(f"  - {col}: {dtype}")

        profile_parts.append("\nMissing Values:")
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                pct = (count / len(df)) * 100
                profile_parts.append(f"  - {col}: {count} ({pct:.1f}%)")

        profile_parts.append("\nDuplicates:")
        dup_count = df.duplicated().sum()
        profile_parts.append(f"  Total duplicate rows: {dup_count}")

        return "\n".join(profile_parts)

