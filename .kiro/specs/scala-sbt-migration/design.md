# Design Document

## Overview

The Scala SBT migration will transform the existing Java-based Confluence2Jira project into a modern Scala application using functional programming principles. The design leverages Scala's type system, immutable data structures, and functional composition to create a more maintainable and robust integration tool. SBT will provide modern build automation, dependency management, and testing capabilities.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Confluence2Jira Scala App               │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                          │
│  ├── CLI Interface                                          │
│  ├── Configuration Management                               │
│  └── Main Application Logic                                 │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                              │
│  ├── Confluence Service (HTTP Client)                       │
│  ├── Jira Service (HTTP Client)                            │
│  ├── Transformation Service                                 │
│  └── Migration Orchestrator                                │
├─────────────────────────────────────────────────────────────┤
│  Domain Layer                                               │
│  ├── Domain Models (Case Classes)                          │
│  ├── Business Logic (Pure Functions)                       │
│  └── Validation Rules                                      │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ├── HTTP Client (sttp)                                    │
│  ├── JSON Serialization (Circe)                           │
│  ├── Configuration (PureConfig)                            │
│  └── Logging (Logback + Scala Logging)                    │
└─────────────────────────────────────────────────────────────┘
```

### Functional Architecture Principles

- **Pure Functions**: Core business logic implemented as pure functions for testability
- **Immutable Data**: All domain models as immutable case classes
- **Error Handling**: Using Either/Try monads for explicit error handling
- **Effect Management**: IO operations wrapped in appropriate effect types
- **Composition**: Small, composable functions that can be easily tested and reused

## Components and Interfaces

### 1. Domain Models

```scala
// Core domain models as case classes
case class ConfluencePage(
  id: String,
  title: String,
  content: String,
  spaceKey: String,
  version: Int,
  lastModified: Instant
)

case class JiraIssue(
  key: Option[String],
  summary: String,
  description: String,
  issueType: String,
  project: String,
  priority: Priority
)

case class MigrationResult(
  sourceId: String,
  targetId: Option[String],
  status: MigrationStatus,
  errors: List[String]
)
```

### 2. Service Interfaces

```scala
trait ConfluenceService[F[_]] {
  def getPage(pageId: String): F[Either[ConfluenceError, ConfluencePage]]
  def getPages(spaceKey: String): F[Either[ConfluenceError, List[ConfluencePage]]]
  def searchPages(query: String): F[Either[ConfluenceError, List[ConfluencePage]]]
}

trait JiraService[F[_]] {
  def createIssue(issue: JiraIssue): F[Either[JiraError, JiraIssue]]
  def updateIssue(issueKey: String, issue: JiraIssue): F[Either[JiraError, JiraIssue]]
  def getIssue(issueKey: String): F[Either[JiraError, JiraIssue]]
}

trait TransformationService {
  def confluenceToJira(page: ConfluencePage): Either[TransformationError, JiraIssue]
  def transformContent(content: String): Either[TransformationError, String]
}
```

### 3. Configuration Management

```scala
case class AppConfig(
  confluence: ConfluenceConfig,
  jira: JiraConfig,
  migration: MigrationConfig
)

case class ConfluenceConfig(
  baseUrl: String,
  username: String,
  apiToken: String,
  spaceKey: String
)

case class JiraConfig(
  baseUrl: String,
  username: String,
  apiToken: String,
  projectKey: String
)
```

## Data Models

### Core Data Flow

1. **Input**: Confluence pages retrieved via REST API
2. **Transformation**: Content converted from Confluence markup to Jira format
3. **Output**: Jira issues created via REST API
4. **Tracking**: Migration results stored for audit and retry capabilities

### JSON Serialization

Using Circe for automatic derivation of JSON codecs:

```scala
import io.circe.generic.auto._
import io.circe.syntax._

// Automatic JSON encoding/decoding for case classes
implicit val confluencePageDecoder: Decoder[ConfluencePage] = deriveDecoder
implicit val jiraIssueEncoder: Encoder[JiraIssue] = deriveEncoder
```

### Error Types

```scala
sealed trait AppError
case class ConfluenceError(message: String, cause: Option[Throwable]) extends AppError
case class JiraError(message: String, statusCode: Int) extends AppError
case class TransformationError(message: String, field: String) extends AppError
case class ConfigurationError(message: String) extends AppError
```

## Error Handling

### Functional Error Handling Strategy

- **Either Type**: For operations that can fail with known error types
- **Try Type**: For operations that might throw exceptions
- **Validation**: For accumulating multiple validation errors
- **Effect Types**: For managing side effects and async operations

```scala
// Example error handling pattern
def migratePage(pageId: String): IO[Either[AppError, MigrationResult]] = {
  for {
    page <- confluenceService.getPage(pageId)
    jiraIssue <- page.traverse(transformationService.confluenceToJira)
    result <- jiraIssue.traverse(jiraService.createIssue)
  } yield result.map(issue => MigrationResult(pageId, Some(issue.key.get), Success, Nil))
}
```

## Testing Strategy

### Testing Framework Stack

- **ScalaTest**: Primary testing framework with FlatSpec style
- **ScalaCheck**: Property-based testing for data transformations
- **Mockito Scala**: Mocking for external service dependencies
- **TestContainers**: Integration testing with real HTTP services

### Test Structure

```
src/test/scala/
├── unit/
│   ├── service/
│   ├── transformation/
│   └── model/
├── integration/
│   ├── confluence/
│   └── jira/
└── property/
    └── transformation/
```

### Testing Approach

1. **Unit Tests**: Pure functions and business logic
2. **Integration Tests**: HTTP client interactions with mock servers
3. **Property Tests**: Data transformation correctness
4. **Contract Tests**: API response parsing and serialization

### Example Test Structure

```scala
class TransformationServiceSpec extends AnyFlatSpec with Matchers {
  "TransformationService" should "convert Confluence page to Jira issue" in {
    val page = ConfluencePage("123", "Test Page", "Content", "SPACE", 1, Instant.now)
    val result = transformationService.confluenceToJira(page)
    
    result shouldBe a[Right[_, _]]
    result.right.get.summary shouldEqual "Test Page"
  }
}
```

## Build Configuration

### SBT Build Structure

```scala
// build.sbt
ThisBuild / scalaVersion := "2.13.12"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.company"

lazy val root = (project in file("."))
  .settings(
    name := "confluence2jira",
    libraryDependencies ++= Dependencies.all,
    scalacOptions ++= CompilerOptions.all
  )
```

### Key Dependencies

- **HTTP Client**: sttp for type-safe HTTP requests
- **JSON**: Circe for functional JSON processing
- **Configuration**: PureConfig for type-safe configuration
- **Logging**: Logback with Scala Logging
- **Testing**: ScalaTest, ScalaCheck, Mockito

### Compiler Options

```scala
object CompilerOptions {
  val all = Seq(
    "-deprecation",
    "-feature",
    "-unchecked",
    "-Xlint",
    "-Ywarn-dead-code",
    "-Ywarn-numeric-widen",
    "-Ywarn-value-discard"
  )
}
```