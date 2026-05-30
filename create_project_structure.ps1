# create_project_structure.ps1
# Run this script from the root of your project (e.g., stock-predictor/)
# It will create the complete professional folder structure with placeholder files.

$root = Get-Location

Write-Host "Creating project structure in: $root" -ForegroundColor Green

# Define all directories (relative to root)
$directories = @(
    ".github/workflows",
    "config",
    "data/external",
    "data/interim",
    "data/processed",
    "data/raw",
    "docs/api",
    "docs/guides",
    "models/checkpoints",
    "models/final",
    "notebooks/exploratory",
    "notebooks/experiments",
    "notebooks/reports",
    "references",
    "reports/figures",
    "reports/metrics",
    "scripts",
    "src/stock_predictor/api/routers",
    "src/stock_predictor/backtesting",
    "src/stock_predictor/data",
    "src/stock_predictor/features",
    "src/stock_predictor/models",
    "src/stock_predictor/evaluation",
    "src/stock_predictor/utils",
    "tests/test_data",
    "tests/test_features",
    "tests/test_models",
    "tests/test_api"
)

# Create directories
foreach ($dir in $directories) {
    $fullPath = Join-Path $root $dir
    New-Item -ItemType Directory -Force -Path $fullPath | Out-Null
    Write-Host "  Created: $dir" -ForegroundColor Cyan
}

# Create __init__.py files in all Python packages
$initFiles = @(
    "src/stock_predictor/__init__.py",
    "src/stock_predictor/api/__init__.py",
    "src/stock_predictor/backtesting/__init__.py",
    "src/stock_predictor/data/__init__.py",
    "src/stock_predictor/features/__init__.py",
    "src/stock_predictor/models/__init__.py",
    "src/stock_predictor/evaluation/__init__.py",
    "src/stock_predictor/utils/__init__.py",
    "tests/__init__.py"
)

foreach ($file in $initFiles) {
    $fullPath = Join-Path $root $file
    New-Item -ItemType File -Force -Path $fullPath | Out-Null
    Write-Host "  Created: $file" -ForegroundColor Cyan
}

# Create placeholder files with minimal content
$placeholderFiles = @{
    ".github/workflows/test.yml" = @"
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
"@
    ".github/workflows/deploy.yml" = @"
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Add your deploy steps here"
"@
    "config/default.yaml" = @"
# Default configuration
data:
  raw_path: data/raw
  processed_path: data/processed
model:
  lstm_units: 50
  epochs: 100
training:
  batch_size: 32
  validation_split: 0.2
"@
    "config/production.yaml" = @"
# Production overrides
data:
  raw_path: /prod/data/raw
model:
  epochs: 200
"@
    "config/logging.yaml" = @"
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
root:
  level: INFO
  handlers: [console]
"@
    "docs/index.md" = "# Project Documentation\n\nWelcome to the stock predictor documentation."
    ".env.example" = @"
# Environment variables example
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:pass@localhost/db
LOG_LEVEL=INFO
"@
    ".gitignore" = @"
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Data & models
data/raw/*
data/interim/*
data/processed/*
!data/raw/.gitkeep
!data/interim/.gitkeep
!data/processed/.gitkeep
models/checkpoints/*
models/final/*
!models/checkpoints/.gitkeep
!models/final/.gitkeep

# Notebooks
.ipynb_checkpoints/
*.ipynb

# IDE
.vscode/
.idea/

# Environment
.env
.venv

# Logs
*.log
"@
    ".pre-commit-config.yaml" = @"
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
"@
    ".python-version" = "3.10.0"
    "docker-compose.yml" = @"
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
"@
    "Dockerfile" = @"
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "stock_predictor.api.main"]
"@
    "Makefile" = @"
.PHONY: install test lint train serve

install:
	pip install -r requirements.txt

test:
	pytest tests/

lint:
	flake8 src/ tests/

train:
	python -m stock_predictor.models.trainer

serve:
	uvicorn stock_predictor.api.main:app --reload
"@
    "pyproject.toml" = @"
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "stock_predictor"
version = "0.1.0"
description = "Stock price prediction using LSTM"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.24",
    "pandas>=2.0",
    "scikit-learn>=1.2",
    "tensorflow>=2.13",
    "fastapi>=0.100",
    "uvicorn>=0.23",
    "pyyaml>=6.0",
    "pytest>=7.0"
]
"@
    "README.md" = "# Stock Predictor\n\nProfessional stock prediction project using LSTM.\n\n## Setup\n\n```bash\nmake install\n```\n\n## Usage\n\n```bash\nmake train\nmake serve\n```\n"
    "requirements.txt" = @"
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.2.2
tensorflow==2.13.0
fastapi==0.100.0
uvicorn==0.23.2
pyyaml==6.0
pytest==7.4.0
"@
    "setup.cfg" = @"
[flake8]
max-line-length = 88
extend-ignore = E203
exclude = .git,__pycache__,venv,.venv,build,dist

[isort]
profile = black
line_length = 88
"@
    "scripts/download_data.py" = @"
#!/usr/bin/env python
\"\"\"Download stock data from Yahoo Finance or other source.\"\"\"
print("Downloading data...")
# Add your implementation
"@
    "scripts/clean_cache.py" = @"
#!/usr/bin/env python
\"\"\"Clean cache and temporary files.\"\"\"
import shutil
from pathlib import Path
cache_dir = Path("data/cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
    print("Cache cleaned.")
"@
    "scripts/show-tree.ps1" = @"
# Your original tree script can be placed here
Write-Host "Tree view script"
"@
    "tests/conftest.py" = @"
import pytest
from stock_predictor.data.collector import DataCollector

@pytest.fixture
def sample_data():
    return {"AAPL": [150, 152, 151]}
"@
    # Add .gitkeep files to keep empty directories under version control
    "data/raw/.gitkeep" = ""
    "data/interim/.gitkeep" = ""
    "data/processed/.gitkeep" = ""
    "models/checkpoints/.gitkeep" = ""
    "models/final/.gitkeep" = ""
}

foreach ($filePath in $placeholderFiles.Keys) {
    $fullPath = Join-Path $root $filePath
    $content = $placeholderFiles[$filePath]
    # Create directory for the file if it doesn't exist
    $dir = Split-Path $fullPath -Parent
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    # Write content (UTF8 without BOM)
    [System.IO.File]::WriteAllText($fullPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  Created: $filePath" -ForegroundColor Yellow
}

Write-Host "`n✅ Project structure created successfully!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. cd $root" -ForegroundColor Cyan
Write-Host "  2. git init" -ForegroundColor Cyan
Write-Host "  3. Copy your existing code into src/stock_predictor/" -ForegroundColor Cyan
Write-Host "  4. Run 'pip install -r requirements.txt'" -ForegroundColor Cyan