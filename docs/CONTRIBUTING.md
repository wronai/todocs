# Contributing to todocs

## Development Setup

```bash
git clone https://github.com/wronai/todocs
cd todocs
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Add or update tests
4. Run the test suite
5. Submit a pull request

## Testing

```bash
python -m unittest discover tests/
```

## Code Style

Follow PEP 8 conventions.

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass before submitting
- Use descriptive commit messages
