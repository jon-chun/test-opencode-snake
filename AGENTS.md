# Agent Instructions

This document provides instructions for AI coding agents operating in this repository.

## Commands

- **Install dependencies**: `pip install -r requirements.txt` (Note: This file is currently empty as there are no external dependencies).
- **Run tests**: `pytest` (Note: No tests have been implemented yet).
- **Run a single test**: `pytest tests/test_file.py::test_function`
- **Run linter**: `ruff check .`
- **Run formatter**: `ruff format .`

## Code Style

- **Imports**: Use `isort` compatible import order (standard library, third-party, first-party).
- **Formatting**: Use `ruff` for formatting.
- **Types**: Use type hints for all function signatures.
- **Naming Conventions**: Use `snake_case` for variables and functions, and `PascalCase` for classes.
- **Error Handling**: Use `try...except` blocks for error handling. Raise specific exceptions instead of generic ones.
- **Docstrings**: Use Google-style docstrings for all public modules, classes, and functions.
