from __future__ import annotations

from typing import Any

from atlassian import Confluence
from jira import JIRA

from confluence2jira.config import Settings
from confluence2jira.models import ConfluencePage, MigrationResult
from confluence2jira.transform import issue_fields


class Migrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.confluence = Confluence(
            url=settings.confluence_url,
            username=settings.confluence_username,
            password=settings.confluence_api_token,
            cloud=True,
        )
        self.jira = JIRA(
            server=settings.jira_url,
            basic_auth=(settings.jira_username, settings.jira_api_token),
        )

    def get_page(self, page_id: str) -> ConfluencePage:
        raw: dict[str, Any] = self.confluence.get_page_by_id(
            page_id, expand="body.storage,_links"
        )
        links = raw.get("_links", {})
        web_ui = links.get("webui")
        url = f"{self.settings.confluence_url.rstrip('/')}{web_ui}" if web_ui else None
        return ConfluencePage(
            page_id=str(raw["id"]),
            title=raw["title"],
            body=raw.get("body", {}).get("storage", {}).get("value", ""),
            url=url,
        )

    def migrate_page(
        self, page_id: str, issue_type: str = "Task", *, dry_run: bool = False
    ) -> MigrationResult:
        page = self.get_page(page_id)
        fields = issue_fields(page, self.settings.jira_project_key, issue_type)
        if dry_run:
            return MigrationResult(page.page_id, None, page.title, dry_run=True)
        issue = self.jira.create_issue(fields=fields)
        return MigrationResult(page.page_id, issue.key, page.title)
