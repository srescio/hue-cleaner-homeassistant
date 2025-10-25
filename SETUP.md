# Development Setup

## Prerequisites
- Python 3.8+ (for component development)

## Setup
1. Install dependencies:
   ```bash
   pip install pre-commit commitizen
   ```

2. Setup git hooks:
   ```bash
   pre-commit install --hook-type commit-msg
   ```

## Commit Messages
This project enforces Conventional Commits via pre-commit + commitizen.

Format: `<type>(<scope>): <description>`

Examples:
- `feat: add Hue Cleaner component`
- `fix(coordinator): handle API timeout`
- `docs: update README`

## Testing
```bash
python test_component.py
```
