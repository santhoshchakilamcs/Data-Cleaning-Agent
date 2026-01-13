# 🧹 Auto-Janitor: AI-Powered Data Cleaning Agent

An autonomous AI agent that automatically cleans and transforms messy datasets using LLMs (OpenAI GPT-4, Anthropic Claude). Built with LangGraph for intelligent, multi-step data cleaning workflows.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

## ✨ Features

- **🤖 Intelligent Data Understanding** - Automatically analyzes your dataset to understand its business context
- **📋 Smart Cleaning Plans** - Generates step-by-step cleaning plans based on detected issues
- **🔒 Safe Execution** - Runs cleaning code in a sandboxed environment with rollback support
- **🔄 Preserves Business Logic** - Understands that negative quantities = returns, not errors
- **📊 Multiple Data Issues Handled**:
  - Missing values (with smart imputation)
  - Inconsistent formats (dates, phone numbers, emails)
  - Currency symbols in numeric fields (`$19.99` → `19.99`)
  - Whitespace trimming
  - Case normalization
  - Email validation
  - And much more!

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/santhoshchakilamcs/Data-Cleaning-Agent.git
cd Data-Cleaning-Agent

# Install dependencies
pip install -r requirements.txt

# Set up your API key
export OPENAI_API_KEY="your-api-key"
# OR
export ANTHROPIC_API_KEY="your-api-key"
```

### Basic Usage

```python
from auto_janitor import AutoJanitor
import pandas as pd

# Load your messy data
df = pd.read_csv("messy_data.csv")

# Create the cleaning agent
janitor = AutoJanitor(provider="openai")  # or "anthropic"

# Clean the data
cleaned_df = janitor.clean(df)

# Save the results
cleaned_df.to_csv("cleaned_data.csv", index=False)
```

### Using LangGraph Agent (Recommended)

```python
from auto_janitor.langgraph_agent import DataCleaningAgent
import pandas as pd

# Load data
df = pd.read_csv("complex_sales_data.csv")

# Create agent
agent = DataCleaningAgent(provider="openai")

# Run the cleaning pipeline
result = agent.run(df)

# Access cleaned data
cleaned_df = result["df"]
```

## 📁 Project Structure

```
auto-janitor/
├── auto_janitor/
│   ├── __init__.py
│   ├── agent.py           # Core AutoJanitor class
│   ├── langgraph_agent.py # LangGraph-based agent
│   ├── sandbox.py         # Safe code execution
│   ├── llm.py             # LLM provider abstraction
│   └── config.py          # Configuration
├── data/
│   ├── input/             # Sample input datasets
│   └── output/            # Cleaned output (gitignored)
├── examples/              # Usage examples
├── tests/                 # Test suite
├── requirements.txt
└── pyproject.toml
```

## 🧪 Running Tests

```bash
# Run the test suite
pytest tests/

# Test with a complex dataset
python test_complex_dataset.py
```

## 🔧 Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_PROVIDER=openai
```

## 📊 Example: Cleaning Sales Data

Input data with issues:
- Prices with `$` symbols
- Missing customer names
- Inconsistent email casing
- Mixed date formats
- Negative quantities (returns)

The agent automatically:
1. Removes `$` and converts to numeric
2. Extracts names from email addresses
3. Normalizes emails to lowercase
4. Parses multiple date formats
5. Preserves negative quantities as valid returns

## 🤝 Contributing

**We welcome contributions from the community!** 

Whether you're fixing bugs, adding new features, improving documentation, or sharing ideas — your help is appreciated!

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions

- 🧹 Add support for more data cleaning patterns
- 🔌 Integrate additional LLM providers (Gemini, Llama, etc.)
- 📊 Add support for more file formats (Excel, Parquet, JSON)
- 🧪 Improve test coverage
- 📚 Enhance documentation and examples
- 🐛 Fix bugs and improve error handling
- ⚡ Performance optimizations

### Code Style

- Write tests for new features

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by OpenAI and Anthropic APIs
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output

---

**⭐ If you find this project useful, please give it a star!**

**💬 Questions or suggestions? Open an issue or start a discussion!**

