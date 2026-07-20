# Codex Repository Instructions

## Project

`confluence2jira` is a Python 3.12 command-line application that reads Confluence pages and
creates Jira issues. It uses `atlassian-python-api` for Confluence, `jira` for Jira,
Beautiful Soup for content conversion, and `uv` for packaging and dependency management.

## Repository Layout

- `src/confluence2jira/`: application package
- `tests/`: pytest test suite
- `pyproject.toml`: package metadata, dependencies, and tool configuration
- `uv.lock`: reproducible dependency lockfile
- `.env.example`: environment variable template without real credentials
- `.kiro/specs/`: requirements, design, and implementation plans

## Commands

Run commands from the repository root:

```text
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run confluence2jira --help
```

Run `uv run pytest` and `uv run ruff check .` before completing code changes. Also run the
formatter check when changing Python files.

## Implementation Guidelines

- Support Python 3.12 and use modern type annotations.
- Keep configuration, API clients, transformation logic, domain models, and CLI orchestration
  separated according to the existing module structure.
- Prefer small, typed functions and immutable value objects where practical.
- Preserve existing CLI behavior unless a task explicitly requires a breaking change.
- Use `--dry-run` when checking behavior with real Confluence data unless remote Jira writes are
  explicitly requested.
- Convert third-party API failures into concise, actionable user-facing errors.
- Do not add a dependency when the standard library or an existing dependency is sufficient.
- When dependencies change, update both `pyproject.toml` and `uv.lock`.

## Testing Guidelines

- Add or update pytest tests for every behavior change.
- Mock Confluence and Jira boundaries; automated tests must not require network access or live
  Atlassian credentials.
- Cover malformed input, missing configuration, transformation edge cases, and remote API errors
  when relevant.
- Keep tests deterministic and independent of execution order.

## Security and Change Hygiene

- Never commit `.env`, API tokens, passwords, authorization headers, or production content.
- Do not log secrets or complete payloads that may contain sensitive page content.
- Do not edit generated caches or virtual environments.
- Keep changes scoped to the request and preserve unrelated working-tree changes.
- Update `README.md`, `.env.example`, and specs when user-facing commands or configuration change.
