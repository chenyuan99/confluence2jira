# Repository Agent Guide

## Project overview

`confluence2jira` is a Scala command-line application intended to move or synchronize content from Confluence to Jira. The project currently contains the sbt build scaffold; application and test sources have not been added yet.

## Technology

- Scala 2.13.12
- sbt 1.9.8
- sttp for HTTP clients
- Circe for JSON
- PureConfig for configuration
- scopt for command-line parsing
- ScalaTest, ScalaCheck, and Mockito Scala for tests

## Repository layout

- `build.sbt`: root project settings and compiler options
- `project/Dependencies.scala`: dependency versions and declarations
- `project/build.properties`: pinned sbt version
- `src/main/scala/`: production Scala sources
- `src/main/resources/`: runtime configuration and resources
- `src/test/scala/`: tests
- `target/` and `project/target/`: generated build output; do not edit or commit

## Development commands

Run these commands from the repository root:

```text
sbt compile
sbt test
sbt run
sbt clean
```

Before considering a change complete, run `sbt test`. Use `sbt compile` as a quicker check while iterating.

## Coding guidelines

- Follow the existing Scala compiler warnings configured in `build.sbt`; resolve new warnings rather than suppressing them without a clear reason.
- Prefer small, focused types and functions. Keep Confluence API concerns, Jira API concerns, mapping logic, and CLI orchestration separate.
- Model expected failures with explicit return types such as `Either` or `Try`; avoid throwing exceptions for normal API or validation errors.
- Do not log access tokens, passwords, authorization headers, or complete payloads that may contain sensitive content.
- Keep blocking work away from asynchronous execution paths. Reuse HTTP clients/backends and close resources cleanly.
- Put dependency versions and declarations in `project/Dependencies.scala`, then include them in `Dependencies.all`.
- Preserve backward compatibility for configuration keys and CLI flags unless the task explicitly calls for a breaking change.

## Testing guidelines

- Mirror production package paths under `src/test/scala`.
- Add unit tests for mapping, validation, parsing, and error handling.
- Mock external systems at the HTTP boundary; tests must not require live Confluence or Jira credentials.
- Include tests for pagination, rate limits, malformed responses, missing fields, and partial failures when relevant.
- Tests run sequentially because `Test / parallelExecution := false` is configured in `build.sbt`.

## Change hygiene

- Keep changes scoped to the request and preserve unrelated user edits.
- Never commit secrets or local IDE files.
- Do not edit generated files under `target/` or `project/target/`.
- Update documentation and example configuration when behavior, CLI options, or configuration keys change.
