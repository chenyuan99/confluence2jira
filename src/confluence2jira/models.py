from dataclasses import dataclass


@dataclass(frozen=True)
class ConfluencePage:
    page_id: str
    title: str
    body: str
    url: str | None = None


@dataclass(frozen=True)
class MigrationResult:
    page_id: str
    issue_key: str | None
    summary: str
    dry_run: bool = False
