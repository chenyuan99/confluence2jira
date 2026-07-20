# confluence2jira

A `uv`-managed Python CLI that reads a Confluence page with
[`atlassian-python-api`](https://atlassian-python-api.readthedocs.io/) and creates a Jira issue
with [`jira`](https://jira.readthedocs.io/).

## Setup

```powershell
uv sync
Copy-Item .env.example .env
```

Load the values from `.env` into your environment. The application intentionally does not read
or commit secrets automatically.

## Usage

Preview a migration without creating a Jira issue:

```powershell
uv run confluence2jira 123456 --dry-run
```

Create an issue:

```powershell
uv run confluence2jira 123456 --issue-type Task
```

## Development

```powershell
uv run pytest
uv run ruff check .
```
