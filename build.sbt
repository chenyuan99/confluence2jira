ThisBuild / scalaVersion := "2.13.12"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.company"

lazy val root = (project in file("."))
  .settings(
    name := "confluence2jira",
    libraryDependencies ++= Dependencies.all,
    scalacOptions ++= CompilerOptions.all,
    Test / parallelExecution := false
  )

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