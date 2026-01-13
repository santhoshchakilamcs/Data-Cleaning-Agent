"""LangGraph-based Auto-Janitor with semantic understanding"""

from typing import TypedDict, Annotated, List, Dict, Any
from operator import add
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from auto_janitor.config import Config
from auto_janitor.sandbox import PythonSandbox


console = Console()


class AgentState(TypedDict):
    """State for the LangGraph agent"""
    df: pd.DataFrame
    original_df: pd.DataFrame
    data_understanding: str
    cleaning_plan: List[Dict[str, str]]
    executed_steps: Annotated[List[Dict[str, Any]], add]
    current_step: int
    errors: Annotated[List[str], add]
    completed: bool
    user_confirmations: Dict[str, bool]


class LangGraphJanitor:
    """LangGraph-based data cleaning agent with semantic understanding"""
    
    def __init__(self, llm_provider: str = None, model: str = None):
        """Initialize the LangGraph agent"""
        provider = llm_provider or Config.LLM_PROVIDER
        model_name = model or Config.MODEL_NAME
        
        if provider == "openai":
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.1,
                api_key=Config.OPENAI_API_KEY
            )
        else:
            self.llm = ChatAnthropic(
                model=model_name,
                temperature=0.1,
                api_key=Config.ANTHROPIC_API_KEY
            )
        
        self.sandbox = None
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand_data", self.understand_data_node)
        workflow.add_node("create_plan", self.create_plan_node)
        workflow.add_node("confirm_plan", self.confirm_plan_node)
        workflow.add_node("execute_step", self.execute_step_node)
        workflow.add_node("validate_results", self.validate_results_node)
        
        # Define edges
        workflow.set_entry_point("understand_data")
        workflow.add_edge("understand_data", "create_plan")
        workflow.add_edge("create_plan", "confirm_plan")
        workflow.add_conditional_edges(
            "confirm_plan",
            self.should_continue_after_confirmation,
            {
                "execute": "execute_step",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "execute_step",
            self.should_continue_execution,
            {
                "continue": "execute_step",
                "validate": "validate_results"
            }
        )
        workflow.add_edge("validate_results", END)
        
        return workflow.compile()

    def understand_data_node(self, state: AgentState) -> AgentState:
        """Node 1: Understand what the data represents semantically"""
        console.print("\n[bold cyan]═══ STEP 1: Understanding Data ═══[/bold cyan]\n")

        df = state["df"]

        # Create data profile
        profile = self._create_detailed_profile(df)

        # Ask LLM to understand the data semantically
        messages = [
            SystemMessage(content="""You are a data analyst. Analyze the provided dataset and explain:
1. What does this data represent? (e.g., sales transactions, user records, etc.)
2. What is the business context?
3. What are the key entities and their relationships?
4. What data quality issues do you see?
5. Which rows appear to be duplicates vs. which are legitimate repeated transactions?

Be specific and detailed."""),
            HumanMessage(content=f"""Analyze this dataset:

{profile}

First few rows:
{df.head(10).to_string()}

Last few rows:
{df.tail(5).to_string()}

Provide a detailed semantic understanding of this data.""")
        ]

        response = self.llm.invoke(messages)
        understanding = response.content

        console.print(Panel(understanding, title="[bold green]Data Understanding[/bold green]", border_style="green"))

        state["data_understanding"] = understanding
        return state

    def create_plan_node(self, state: AgentState) -> AgentState:
        """Node 2: Create a detailed cleaning plan"""
        console.print("\n[bold cyan]═══ STEP 2: Creating Cleaning Plan ═══[/bold cyan]\n")

        messages = [
            SystemMessage(content="""You are a data cleaning expert. Based on the data understanding, create a detailed cleaning plan.

For each cleaning step, specify:
1. step_name: Brief name
2. description: What will be done
3. destructive: true/false (does it remove rows?)
4. requires_confirmation: true/false (needs user decision?)
5. reason: Why this step is necessary
6. code: Python code to execute (use variable 'df')

Return ONLY a valid JSON array of steps. Example:
[
  {
    "step_name": "Standardize prices",
    "description": "Remove $ symbols and convert to numeric",
    "destructive": false,
    "requires_confirmation": false,
    "reason": "Prices need to be numeric for analysis",
    "code": "df['unit_price'] = df['unit_price'].astype(str).str.replace('$', '').str.replace('USD', '').str.replace(',', '.').str.strip()\\ndf['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')"
  }
]

CRITICAL RULES:
- For duplicates, explain which rows are true duplicates vs repeated legitimate transactions
- Only remove rows if absolutely necessary
- Preserve all valid data
- NEVER convert negative quantities to positive - they may represent returns/refunds
- For negative quantities: Add a 'transaction_type' column ('sale' or 'return') instead
- Flag suspicious data, don't auto-correct it
- If unsure about data meaning, set requires_confirmation=true

DATA CLEANING BEST PRACTICES:
1. **Price/Currency Cleaning**: Use pd.to_numeric() with errors='coerce' after removing symbols
   - Handle: $, USD, commas, spaces
   - Example: df['price'] = pd.to_numeric(df['price'].astype(str).str.replace('$', '').str.strip(), errors='coerce')

2. **Missing Names from Emails**: Extract names from email addresses when name is missing
   - Example: df.loc[df['name'].isna(), 'name'] = df.loc[df['name'].isna(), 'email'].str.split('@').str[0].str.replace('.', ' ').str.title()

3. **Email Normalization**: Always lowercase emails
   - Example: df['email'] = df['email'].str.lower()

4. **Whitespace**: Strip leading/trailing spaces from ALL text columns
   - Example: df['column'] = df['column'].str.strip()

5. **Categorical Standardization**: Use .str.title() or .str.lower() consistently
   - Example: df['region'] = df['region'].str.strip().str.title()

6. **Date Parsing**: Use pd.to_datetime() with errors='coerce' to handle multiple formats
   - Example: df['date'] = pd.to_datetime(df['date'], errors='coerce')

7. **Phone Numbers**: Standardize to consistent format
   - Example: Extract digits and reformat

8. **Email Validation**: Use .str.contains() with na=False to handle NaN values
   - Example: df['invalid_email'] = ~df['email'].str.contains('@', na=False)
   - AVOID using 'in' operator with lambda on string columns (fails on NaN)

9. **Quantity/Numeric Comparisons**: ALWAYS convert to numeric BEFORE comparing
   - WRONG: df['quantity'].apply(lambda x: 'return' if x < 0 else 'sale')  # Fails if quantity is string
   - CORRECT: df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce'); df['transaction_type'] = df['quantity'].apply(lambda x: 'return' if pd.notna(x) and x < 0 else 'sale')
   - Or use: df['transaction_type'] = np.where(df['quantity'] < 0, 'return', 'sale')

IMPORTANT: When writing regex patterns in JSON code strings, use DOUBLE backslashes (\\\\) for escape sequences!
- Correct: "df['email'].str.contains(r'^[\\\\w\\\\.-]+@[\\\\w\\\\.-]+\\\\.\\\\w+$', na=False)"
- Wrong: "df['email'].str.contains(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$', na=False)"

ALWAYS apply these practices in your cleaning plan!"""),
            HumanMessage(content=f"""Data Understanding:
{state['data_understanding']}

Current data shape: {state['df'].shape}

Create a cleaning plan as a JSON array.""")
        ]

        response = self.llm.invoke(messages)

        # Parse the JSON plan
        import json
        import re

        # Extract JSON from response
        content = response.content
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            plan_json = json_match.group(0)
            try:
                plan = json.loads(plan_json)
            except json.JSONDecodeError as e:
                console.print(f"[red]✗ Error parsing JSON plan: {e}[/red]")
                console.print(f"[yellow]Raw response:[/yellow]\n{content}")
                # Try to fix common JSON issues
                plan_json = plan_json.replace('\\w', '\\\\w').replace('\\d', '\\\\d').replace('\\s', '\\\\s')
                plan_json = plan_json.replace('\\.-', '\\\\.-').replace('\\+', '\\\\+').replace('\\^', '\\\\^')
                try:
                    plan = json.loads(plan_json)
                    console.print("[green]✓ Fixed JSON by escaping regex patterns[/green]")
                except:
                    plan = []
        else:
            plan = []

        state["cleaning_plan"] = plan

        # Display plan
        table = Table(title="Cleaning Plan")
        table.add_column("Step", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Destructive", style="red")

        for i, step in enumerate(plan, 1):
            table.add_row(
                f"{i}. {step['step_name']}",
                step['description'],
                "⚠️  YES" if step.get('destructive') else "✓ No"
            )

        console.print(table)

        return state

    def confirm_plan_node(self, state: AgentState) -> AgentState:
        """Node 3: Get user confirmation for destructive operations"""
        console.print("\n[bold cyan]═══ STEP 3: Confirmation ═══[/bold cyan]\n")

        destructive_steps = [s for s in state["cleaning_plan"] if s.get("destructive")]
        confirmation_steps = [s for s in state["cleaning_plan"] if s.get("requires_confirmation")]

        if destructive_steps:
            console.print("[bold yellow]⚠️  The following steps will REMOVE data:[/bold yellow]\n")
            for step in destructive_steps:
                console.print(f"  • {step['step_name']}: {step['description']}")
                console.print(f"    Reason: {step['reason']}\n")

            response = input("\n[?] Proceed with these destructive operations? (yes/no): ").strip().lower()
            state["user_confirmations"]["destructive_ops"] = response == "yes"

            if response != "yes":
                console.print("[bold red]✗ User cancelled destructive operations[/bold red]")
                state["completed"] = True
                return state

        if confirmation_steps:
            console.print("\n[bold yellow]⚠️  The following steps need your decision:[/bold yellow]\n")
            for step in confirmation_steps:
                console.print(f"  • {step['step_name']}: {step['description']}")
                console.print(f"    Reason: {step['reason']}\n")

            response = input("\n[?] Proceed with these operations? (yes/no): ").strip().lower()
            state["user_confirmations"]["confirmation_ops"] = response == "yes"

            if response != "yes":
                console.print("[bold red]✗ User cancelled operations[/bold red]")
                state["completed"] = True
                return state

        console.print("[bold green]✓ Plan confirmed. Starting execution...[/bold green]")
        state["current_step"] = 0
        state["executed_steps"] = []
        state["errors"] = []
        return state

    def execute_step_node(self, state: AgentState) -> AgentState:
        """Node 4: Execute a single cleaning step"""
        step_idx = state["current_step"]
        plan = state["cleaning_plan"]

        if step_idx >= len(plan):
            return state

        step = plan[step_idx]

        console.print(f"\n[bold magenta]═══ Executing Step {step_idx + 1}/{len(plan)}: {step['step_name']} ═══[/bold magenta]\n")
        console.print(f"[yellow]{step['description']}[/yellow]\n")

        # Execute code in sandbox
        if self.sandbox is None:
            self.sandbox = PythonSandbox(state["df"])

        console.print(Syntax(step['code'], "python", theme="monokai", line_numbers=True))

        success, output, result_df = self.sandbox.execute(step['code'])

        if success:
            console.print(f"\n[green]✓ Success:[/green] {output}")
            console.print(f"[dim]Rows: {len(state['df'])} → {len(result_df)}[/dim]")
            state["df"] = result_df
            self.sandbox.update_dataframe(result_df)

            state["executed_steps"].append({
                "step": step_idx + 1,
                "name": step['step_name'],
                "success": True,
                "rows_before": len(state["df"]),
                "rows_after": len(result_df)
            })
        else:
            console.print(f"\n[red]✗ Error:[/red]\n{output}")
            state["errors"].append(f"Step {step_idx + 1} failed: {output}")

        state["current_step"] += 1
        return state

    def validate_results_node(self, state: AgentState) -> AgentState:
        """Node 5: Validate final results"""
        console.print("\n[bold cyan]═══ STEP 5: Validation ═══[/bold cyan]\n")

        original_rows = len(state["original_df"])
        final_rows = len(state["df"])

        console.print(f"[bold]Original rows:[/bold] {original_rows}")
        console.print(f"[bold]Final rows:[/bold] {final_rows}")
        console.print(f"[bold]Rows removed:[/bold] {original_rows - final_rows}\n")

        if state["errors"]:
            console.print("[bold red]Errors encountered:[/bold red]")
            for error in state["errors"]:
                console.print(f"  • {error}")
        else:
            console.print("[bold green]✓ All steps completed successfully![/bold green]")

        state["completed"] = True
        return state

    def should_continue_after_confirmation(self, state: AgentState) -> str:
        """Decide whether to proceed after confirmation"""
        if state.get("completed"):
            return "end"
        return "execute"

    def should_continue_execution(self, state: AgentState) -> str:
        """Decide next step after execution"""
        # Don't go back to create_plan on errors - just continue to next step
        # This prevents infinite loops when a step fails
        if state["current_step"] >= len(state["cleaning_plan"]):
            return "validate"
        return "continue"

    def _create_detailed_profile(self, df: pd.DataFrame) -> str:
        """Create a detailed data profile"""
        profile = []

        profile.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        profile.append(f"Columns: {', '.join(df.columns.tolist())}")

        profile.append("\nData Types:")
        for col, dtype in df.dtypes.items():
            profile.append(f"  {col}: {dtype}")

        profile.append("\nMissing Values:")
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                pct = (count / len(df)) * 100
                profile.append(f"  {col}: {count} ({pct:.1f}%)")

        profile.append("\nDuplicates:")
        dup_count = df.duplicated().sum()
        profile.append(f"  Total duplicate rows: {dup_count}")
        if dup_count > 0:
            profile.append(f"  Duplicate row indices: {df[df.duplicated(keep=False)].index.tolist()}")

        profile.append("\nValue Distributions (first 3 columns):")
        for col in df.columns[:3]:
            unique_count = df[col].nunique()
            profile.append(f"  {col}: {unique_count} unique values")
            if unique_count <= 10:
                value_counts = df[col].value_counts().head(10)
                for val, count in value_counts.items():
                    profile.append(f"    '{val}': {count}")

        return "\n".join(profile)

    def clean_csv(self, csv_path: str, output_path: str = None) -> pd.DataFrame:
        """Clean a CSV file using LangGraph workflow"""
        console.print(f"\n[bold blue]Loading CSV:[/bold blue] {csv_path}")
        df = pd.read_csv(csv_path)
        console.print(f"[green]✓[/green] Loaded {len(df)} rows, {len(df.columns)} columns\n")

        # Initialize state
        initial_state = {
            "df": df.copy(),
            "original_df": df.copy(),
            "data_understanding": "",
            "cleaning_plan": [],
            "executed_steps": [],
            "current_step": 0,
            "errors": [],
            "completed": False,
            "user_confirmations": {}
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        cleaned_df = final_state["df"]

        # Save if output path provided
        if output_path and not final_state.get("completed"):
            console.print("\n[yellow]⚠️  Cleaning was not completed. Not saving.[/yellow]")
        elif output_path:
            cleaned_df.to_csv(output_path, index=False)
            console.print(f"\n[bold green]✓ Saved cleaned data to:[/bold green] {output_path}")

        return cleaned_df

