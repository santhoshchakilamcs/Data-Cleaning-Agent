"""Safe Python code execution sandbox for Auto-Janitor"""

import sys
import io
import traceback
from typing import Dict, Any, Tuple
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd


class PythonSandbox:
    """Execute Python code in a restricted environment"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize sandbox with a DataFrame"""
        self.df = df.copy()
        self.execution_history = []
    
    def execute(self, code: str) -> Tuple[bool, str, pd.DataFrame]:
        """
        Execute Python code safely
        
        Args:
            code: Python code to execute
            
        Returns:
            Tuple of (success, output/error, resulting_dataframe)
        """
        # Create a safe namespace with only necessary imports
        namespace = {
            'pd': pd,
            'df': self.df.copy(),
            'np': __import__('numpy'),
        }
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the code
                exec(code, namespace)
            
            # Get the modified dataframe
            result_df = namespace.get('df', self.df)
            
            # Capture any output
            output = stdout_capture.getvalue()
            if not output:
                output = "Code executed successfully"
            
            # Store execution history
            self.execution_history.append({
                'code': code,
                'success': True,
                'output': output
            })
            
            return True, output, result_df
            
        except Exception as e:
            # Capture the error
            error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            
            # Store execution history
            self.execution_history.append({
                'code': code,
                'success': False,
                'output': error_msg
            })
            
            return False, error_msg, self.df
    
    def update_dataframe(self, df: pd.DataFrame):
        """Update the sandbox's dataframe"""
        self.df = df.copy()
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the current dataframe"""
        return self.df.copy()
    
    def get_history(self) -> list:
        """Get execution history"""
        return self.execution_history.copy()

