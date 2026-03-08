.PHONY: help install dev test lint format clean build publish

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

dev:  ## Install with dev dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	python -m pytest tests/ -v

test-cov:  ## Run tests with coverage
	python -m pytest tests/ -v --cov=todocs --cov-report=term-missing

lint:  ## Run linters
	ruff check todocs/ tests/

format:  ## Format code
	black todocs/ tests/
	ruff check --fix todocs/ tests/

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info todocs/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean  ## Build distribution
	python -m build

publish: build  ## Publish to PyPI
	python -m twine upload dist/*
