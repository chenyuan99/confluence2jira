# Technology Stack

## Core Technologies
- **Language**: Java 19
- **IDE**: IntelliJ IDEA
- **Build System**: Standard Java compilation (no Maven/Gradle detected yet)

## Development Environment
- JDK 19 required
- IntelliJ IDEA project configuration included
- Git version control

## Common Commands
Since this is a standard Java project without a build tool configured yet:

### Compilation
```bash
javac -d out src/**/*.java
```

### Running
```bash
java -cp out [MainClassName]
```

### Development Setup
1. Open project in IntelliJ IDEA
2. Ensure JDK 19 is configured
3. Source files should be placed in `src/` directory
4. Compiled output goes to `out/` directory

## Future Considerations
- Consider adding Maven or Gradle for dependency management
- Add testing framework (JUnit 5 recommended)
- Configure logging framework (SLF4J + Logback)
- Add Atlassian SDK dependencies for Confluence/Jira integration