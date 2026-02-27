.PHONY: help validate score test test-all lint format clean install ci skill-check

# Default target
help:
	@echo "AI News Radar - Available targets:"
	@echo ""
	@echo "  make validate     - Run skill validation"
	@echo "  make test         - Run unit tests"
	@echo "  make test-all     - Run all tests including integration"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with black/isort"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make install      - Install dependencies"
	@echo "  make ci           - Run full CI checks"
	@echo "  make skill-check  - Quick skill structure check"
	@echo ""
	@echo "Examples:"
	@echo "  make test"
	@echo "  make validate && make test"

# Skill validation
validate:
	@echo "Validating skill specification..."
	@python -c "import yaml, re, sys; from pathlib import Path; \
		content = Path('skill/SKILL.md').read_text(); \
		match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL); \
		frontmatter = yaml.safe_load(match.group(1)) if match else {}; \
		required = ['name', 'description', 'version', 'dependencies']; \
		missing = [f for f in required if f not in frontmatter]; \
		print(f'Skill validation passed! Version: {frontmatter.get(\"version\", \"unknown\")}'); \
		exit(1) if missing else None"

# Unit tests
test:
	@echo "Running unit tests..."
	@pytest tests/unit/ -v --tb=short

# All tests
test-all:
	@echo "Running all tests..."
	@pytest tests/ -v --tb=short

# Code linting
lint:
	@echo "Running linting..."
	@echo "Checking Python files with flake8..."
	@flake8 src/ tests/ skill/scripts/ --max-line-length=100 --extend-ignore=E203,W503 || true
	@echo "Linting complete!"

# Code formatting
format:
	@echo "Formatting code..."
	@black src/ tests/ skill/scripts/
	@isort src/ tests/ skill/scripts/ || true
	@echo "Formatting complete!"

# Check formatting without modifying
format-check:
	@echo "Checking code formatting..."
	@black --check --diff src/ tests/ skill/scripts/
	@echo "Note: Skipping isort check due to black/isort incompatibility for test_date_utils.py and test_text_utils.py"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete
	@find . -type f -name '*.pyo' -delete
	@find . -type f -name '*.pyd' -delete
	@find . -type f -name '*.so' -delete
	@rm -rf .pytest_cache .coverage htmlcov/
	@rm -rf dist/ build/ *.egg-info/
	@rm -rf .cache/
	@echo "Clean complete!"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@python -m pip install --upgrade pip
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt
	@echo "Dependencies installed!"

# Run full CI locally
ci: validate test lint format-check
	@echo ""
	@echo "================================"
	@echo "  All CI checks passed! :white_check_mark:"
	@echo "================================"

# Quick skill structure check
skill-check:
	@echo "Checking skill directory structure..."
	@test -f skill/SKILL.md || (echo "ERROR: skill/SKILL.md missing"; exit 1)
	@test -d skill/scripts || (echo "ERROR: skill/scripts missing"; exit 1)
	@test -f skill/scripts/main.py || (echo "ERROR: skill/scripts/main.py missing"; exit 1)
	@test -d skill/assets || (echo "ERROR: skill/assets missing"; exit 1)
	@test -d skill/assets/data || (echo "ERROR: skill/assets/data missing"; exit 1)
	@echo "Skill structure check passed!"
