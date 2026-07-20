# Design Document

## Overview

The Python 3 migration will transform the existing Java-based Confluence2Jira project into a typed, maintainable Python command-line application. The implementation will use clear module boundaries, immutable domain models, dependency injection, and asynchronous HTTP clients. Standard Python packaging through `pyproject.toml` will provide dependency management, testing, linting, type checking, and distributable artifacts.

The design preserves the existing Confluence-to-Jira workflow while making API interactions, transformations, configuration, and error handling independently testable.

## Architecture

### High-Level Architecture

```text
+------------------------------------------------------------+
|                 Confluence2Jira Python App                 |
+------------------------------------------------------------+
| Application Layer                                          |
| - CLI interface                                            |
| - Configuration loading                                    |
| - Application wiring and lifecycle                         |
+------------------------------------------------------------+
| Service Layer                                              |
| - Confluence service                                       |
| - Jira service                                             |
| - Transformation service                                   |
| - Migration orchestrator                                   |
+------------------------------------------------------------+
| Domain Layer                                               |
| - Immutable domain models                                  |
| - Validation rules                                         |
| - Migration result and error types                         |
+------------------------------------------------------------+
| Infrastructure Layer                                       |
| - HTTP client (httpx)                                      |
| - JSON parsing and validation (Pydantic)                   |
| - Configuration (pydantic-settings)                        |
| - Logging (Python logging)                                 |
+------------------------------------------------------------+
```

### Design Principles

- **Typed boundaries**: All public functions and service interfaces use type annotations and are checked with mypy.
- **Immutable domain data**: Domain objects use frozen dataclasses or immutable Pydantic models.
- **Explicit failures**: Expected API, validation, and transformation failures use application-specific exceptions with structured context.
- **Async I/O**: Confluence and Jira requests use a shared `httpx.AsyncClient`; CPU-only transformation functions remain synchronous.
- **Dependency injection**: The orchestrator depends on protocols rather than concrete HTTP implementations.
- **Pure transformations**: Content conversion and validation avoid I/O and mutable global state.
- **Secure defaults**: Secrets come from the environment or an ignored local file and are never logged.

## Project Structure

```text
confluence2jira/
|-- pyproject.toml
|-- README.md
|-- src/
|   `-- confluence2jira/
|       |-- __init__.py
|       |-- __main__.py
|       |-- cli.py
|       |-- config.py
|       |-- errors.py
|       |-- models.py
|       |-- orchestrator.py
|       |-- transformation.py
|       `-- clients/
|           |-- __init__.py
|           |-- confluence.py
|           `-- jira.py
`-- tests/
    |-- unit/
    |-- integration/
    |-- contract/
    `-- fixtures/
```

The `src` layout prevents imports from accidentally resolving against the repository directory instead of the installed package.

## Components and Interfaces

### 1. Domain Models

Domain models represent normalized application data rather than raw Atlassian API payloads.

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MigrationStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class ConfluencePage:
    id: str
    title: str
    content: str
    space_key: str
    version: int
    last_modified: datetime


@dataclass(frozen=True, slots=True)
class JiraIssue:
    summary: str
    description: str
    issue_type: str
    project_key: str
    priority: str
    key: str | None = None


@dataclass(frozen=True, slots=True)
class MigrationResult:
    source_id: str
    status: MigrationStatus
    target_id: str | None = None
    errors: tuple[str, ...] = field(default_factory=tuple)
```

Raw API responses are validated by Pydantic transport models and converted into these domain types. This prevents API-specific field names and optional values from leaking throughout the application.

### 2. Service Interfaces

`Protocol` definitions allow production clients and test doubles to satisfy the same interfaces without inheritance.

```python
from collections.abc import Sequence
from typing import Protocol


class ConfluenceService(Protocol):
    async def get_page(self, page_id: str) -> ConfluencePage: ...
    async def get_pages(self, space_key: str) -> Sequence[ConfluencePage]: ...
    async def search_pages(self, query: str) -> Sequence[ConfluencePage]: ...


class JiraService(Protocol):
    async def create_issue(self, issue: JiraIssue) -> JiraIssue: ...
    async def update_issue(self, issue_key: str, issue: JiraIssue) -> JiraIssue: ...
    async def get_issue(self, issue_key: str) -> JiraIssue: ...


class TransformationService(Protocol):
    def confluence_to_jira(self, page: ConfluencePage) -> JiraIssue: ...
    def transform_content(self, content: str) -> str: ...
```

### 3. Configuration Management

Pydantic Settings loads configuration from environment variables and optionally from a local `.env` file. Environment variables use the `C2J_` prefix and nested keys use a double underscore, for example `C2J_JIRA__API_TOKEN`.

```python
from pydantic import AnyHttpUrl, BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfluenceConfig(BaseModel):
    base_url: AnyHttpUrl
    username: str
    api_token: SecretStr
    space_key: str


class JiraConfig(BaseModel):
    base_url: AnyHttpUrl
    username: str
    api_token: SecretStr
    project_key: str


class MigrationConfig(BaseModel):
    concurrency: int = 5
    max_retries: int = 3
    dry_run: bool = False


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="C2J_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    confluence: ConfluenceConfig
    jira: JiraConfig
    migration: MigrationConfig = MigrationConfig()
```

Configuration is validated before any API request. Validation errors are converted into concise user-facing messages. Secret values remain wrapped in `SecretStr` and must never be included in logs or serialized output.

## Data Flow

1. The CLI parses the requested migration mode and loads configuration.
2. The Confluence client retrieves one or more pages, following pagination links where necessary.
3. Pydantic transport models validate the response and map it to domain models.
4. The transformation service converts Confluence storage content into Jira-compatible content and validates required fields.
5. The Jira client creates or updates issues unless dry-run mode is enabled.
6. The orchestrator records a `MigrationResult` for every source page.
7. The CLI prints a summary and exits with a status code appropriate to the outcome.

Batch operations use bounded concurrency so that large migrations do not exhaust connections or exceed API limits. Results retain input ordering for predictable reporting.

## HTTP and JSON Handling

- Use one application-scoped `httpx.AsyncClient` with configured timeouts and connection limits.
- Set authentication and standard headers in each Atlassian client without exposing them to callers.
- Follow Confluence pagination until exhausted or until an optional caller-supplied limit is reached.
- Retry transient failures such as HTTP 429 and selected 5xx responses with capped exponential backoff and jitter.
- Honor the `Retry-After` header when present.
- Do not retry authentication failures, validation failures, or other permanent 4xx responses.
- Validate successful response bodies with Pydantic before mapping them to domain models.
- Include service name, operation, status code, and request correlation ID in errors, but omit credentials and sensitive bodies.

## Error Handling

All expected application failures derive from `Confluence2JiraError`.

```python
class Confluence2JiraError(Exception):
    """Base class for expected application failures."""


class ConfigurationError(Confluence2JiraError):
    pass


class ApiError(Confluence2JiraError):
    def __init__(
        self,
        message: str,
        *,
        service: str,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.service = service
        self.status_code = status_code
        self.retryable = retryable


class TransformationError(Confluence2JiraError):
    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field
```

The handling policy is:

- Client methods translate `httpx` and response-validation failures into `ApiError`.
- Transformation functions raise `TransformationError` for invalid source data.
- The batch orchestrator catches expected errors per page, records a failed result, and continues processing other pages.
- Cancellation and unexpected programming errors are not silently converted into migration failures.
- The CLI maps configuration errors, partial failures, and unexpected failures to distinct nonzero exit codes.

Example orchestration:

```python
async def migrate_page(page_id: str) -> MigrationResult:
    try:
        page = await confluence_service.get_page(page_id)
        issue = transformation_service.confluence_to_jira(page)
        created = await jira_service.create_issue(issue)
        return MigrationResult(
            source_id=page_id,
            target_id=created.key,
            status=MigrationStatus.SUCCEEDED,
        )
    except Confluence2JiraError as exc:
        return MigrationResult(
            source_id=page_id,
            status=MigrationStatus.FAILED,
            errors=(str(exc),),
        )
```

## Command-Line Interface

Typer provides the CLI and generated help output. The application is exposed as both `python -m confluence2jira` and a `confluence2jira` console script.

Initial commands:

- `migrate-page PAGE_ID`: migrate one page.
- `migrate-space SPACE_KEY`: migrate all eligible pages in a space.
- `search QUERY`: migrate pages matching a Confluence query.
- `validate-config`: validate configuration without contacting either service.

Common options include `--dry-run`, `--concurrency`, `--max-retries`, and `--verbose`. Destructive or remote-writing commands clearly report dry-run status before processing.

## Testing Strategy

### Testing Tooling

- **pytest**: Test runner and fixtures.
- **pytest-asyncio**: Async service and orchestrator tests.
- **Hypothesis**: Property-based tests for content transformations.
- **respx**: Mocked `httpx` requests for client and contract tests.
- **pytest-cov**: Coverage measurement and reports.
- **mypy**: Static type checking.
- **Ruff**: Linting and formatting checks.

### Test Structure

```text
tests/
|-- unit/
|   |-- test_models.py
|   |-- test_transformation.py
|   |-- test_config.py
|   `-- test_orchestrator.py
|-- integration/
|   |-- test_confluence_client.py
|   `-- test_jira_client.py
|-- contract/
|   `-- test_api_payloads.py
`-- fixtures/
    |-- confluence/
    `-- jira/
```

### Testing Approach

1. **Unit tests** cover pure transformations, validation, orchestration, and exit-code behavior.
2. **HTTP integration tests** use `respx` to verify URLs, authentication, pagination, retries, timeouts, and error mapping without live credentials.
3. **Property tests** verify invariants such as deterministic transformations and output-length constraints.
4. **Contract tests** validate representative saved Confluence and Jira payloads against transport models.
5. **Optional live smoke tests** are explicitly selected and skipped unless dedicated test credentials are present.

Tests must cover malformed JSON, missing fields, pagination, rate limiting, permission errors, partial batch failures, and secret redaction.

## Packaging and Tool Configuration

Project metadata and tools are configured in `pyproject.toml`. A PEP 517-compatible build backend such as Hatchling produces wheels and source distributions.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "confluence2jira"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "httpx",
  "pydantic>=2",
  "pydantic-settings",
  "typer",
]

[project.scripts]
confluence2jira = "confluence2jira.cli:app"

[project.optional-dependencies]
dev = [
  "hypothesis",
  "mypy",
  "pytest",
  "pytest-asyncio",
  "pytest-cov",
  "respx",
  "ruff",
]
```

Dependency versions must be locked by the selected environment tool and updated deliberately. Runtime code must not depend on development-only packages.

## Quality Gates

The following commands must pass before a change is complete:

```text
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m build
```

CI runs the same checks on supported Python versions. Coverage should focus on critical transformation and orchestration paths rather than excluding difficult code solely to meet a numeric target.

## Logging and Observability

- Use the standard `logging` package with structured context fields.
- Default to human-readable console output; optionally support JSON logs for automated environments.
- Assign a migration run ID and include page and issue identifiers where available.
- Record counts, duration, retries, and final status without logging page bodies or credentials.
- Use `DEBUG` for sanitized request metadata, `INFO` for progress, `WARNING` for recoverable failures, and `ERROR` for failed operations.

## Security Considerations

- Read API tokens from environment variables or a secret manager; `.env` is for local development only and must be ignored by Git.
- Never print token values, authorization headers, or full sensitive payloads.
- Use TLS verification by default. Any opt-out must require an explicit development-only option and warning.
- Apply least-privilege Atlassian permissions to migration accounts.
- Sanitize remote error bodies before including them in logs or CLI output.
- Avoid persisting source content unless audit storage is explicitly enabled and secured.
