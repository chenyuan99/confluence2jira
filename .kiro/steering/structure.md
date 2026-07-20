# Project Structure

## Current Organization
```
confluence2jira/
├── .git/                 # Git repository metadata
├── .idea/                # IntelliJ IDEA project configuration
├── .kiro/                # Kiro AI assistant configuration
│   └── steering/         # AI guidance documents
├── out/                  # Compiled Java classes (generated)
└── src/                  # Source code (to be created)
```

## Recommended Source Structure
When adding source code, follow standard Java conventions:

```
src/
├── main/
│   └── java/
│       └── com/
│           └── [company]/
│               └── confluence2jira/
│                   ├── Main.java
│                   ├── config/
│                   ├── service/
│                   ├── model/
│                   └── util/
└── test/
    └── java/
        └── com/
            └── [company]/
                └── confluence2jira/
```

## Package Conventions
- Use reverse domain naming: `com.[company].confluence2jira`
- Separate concerns into logical packages:
  - `config/` - Configuration classes
  - `service/` - Business logic and API interactions
  - `model/` - Data models and DTOs
  - `util/` - Utility classes and helpers

## File Naming
- Use PascalCase for class names
- Use camelCase for method and variable names
- Use UPPER_SNAKE_CASE for constants
- Test classes should end with `Test` suffix

## Build Artifacts
- `out/` directory contains compiled classes (gitignored)
- Keep source and compiled code separate
- Consider adding `target/` or `build/` when build tools are added