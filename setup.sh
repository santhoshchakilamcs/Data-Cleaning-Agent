#!/bin/bash

echo "Setting up Auto-Janitor..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
    echo ""
fi

echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)"
echo "2. Run: poetry run python examples/basic_usage.py"

