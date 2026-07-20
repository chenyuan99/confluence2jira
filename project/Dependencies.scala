import sbt._

object Dependencies {
  
  // Versions
  object Versions {
    val circe = "0.14.6"
    val sttp = "3.9.1"
    val pureConfig = "0.17.4"
    val scalaLogging = "3.9.5"
    val logback = "1.4.11"
    val scalaTest = "3.2.17"
    val scalaCheck = "1.17.0"
    val mockito = "1.17.14"
    val scopt = "4.1.0"
  }
  
  // HTTP Client
  val sttpCore = "com.softwaremill.sttp.client3" %% "core" % Versions.sttp
  val sttpCirce = "com.softwaremill.sttp.client3" %% "circe" % Versions.sttp
  val sttpAsync = "com.softwaremill.sttp.client3" %% "async-http-client-backend-future" % Versions.sttp
  
  // JSON Processing
  val circeCore = "io.circe" %% "circe-core" % Versions.circe
  val circeGeneric = "io.circe" %% "circe-generic" % Versions.circe
  val circeParser = "io.circe" %% "circe-parser" % Versions.circe
  
  // Configuration
  val pureConfig = "com.github.pureconfig" %% "pureconfig" % Versions.pureConfig
  
  // Logging
  val scalaLogging = "com.typesafe.scala-logging" %% "scala-logging" % Versions.scalaLogging
  val logback = "ch.qos.logback" % "logback-classic" % Versions.logback
  
  // CLI
  val scopt = "com.github.scopt" %% "scopt" % Versions.scopt
  
  // Testing
  val scalaTest = "org.scalatest" %% "scalatest" % Versions.scalaTest % Test
  val scalaCheck = "org.scalacheck" %% "scalacheck" % Versions.scalaCheck % Test
  val mockitoScala = "org.mockito" %% "mockito-scala" % Versions.mockito % Test
  
  // All dependencies
  val all = Seq(
    sttpCore,
    sttpCirce,
    sttpAsync,
    circeCore,
    circeGeneric,
    circeParser,
    pureConfig,
    scalaLogging,
    logback,
    scopt,
    scalaTest,
    scalaCheck,
    mockitoScala
  )
}