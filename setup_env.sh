#!/bin/bash
set -e

echo "Setting up environment for Novel Scenification..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
else
  echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements and ipykernel
echo "Installing requirements and ipykernel..."
pip install -r requirements.txt ipykernel

# Register kernel
echo "Registering Jupyter kernel..."
python -m ipykernel install \
  --user \
  --name novel-scenification \
  --display-name "Python (Novel Scenification)"

echo "Setup complete!" 