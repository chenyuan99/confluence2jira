from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import confluence2jira.clients as clients
from confluence2jira.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        confluence_url="https://confluence.example.com/",
        confluence_username="confluence-user",
        confluence_api_token="confluence-token",
        jira_url="https://jira.example.com",
        jira_username="jira-user",
        jira_api_token="jira-token",
        jira_project_key="DEMO",
    )


@pytest.fixture
def migrator(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> tuple[clients.Migrator, Mock, Mock]:
    confluence = Mock()
    jira = Mock()
    confluence_constructor = Mock(return_value=confluence)
    jira_constructor = Mock(return_value=jira)
    monkeypatch.setattr(clients, "Confluence", confluence_constructor)
    monkeypatch.setattr(clients, "JIRA", jira_constructor)

    instance = clients.Migrator(settings)

    confluence_constructor.assert_called_once_with(
        url=settings.confluence_url,
        username=settings.confluence_username,
        password=settings.confluence_api_token,
        cloud=True,
    )
    jira_constructor.assert_called_once_with(
        server=settings.jira_url,
        basic_auth=(settings.jira_username, settings.jira_api_token),
    )
    return instance, confluence, jira


def test_get_page_maps_confluence_response_and_builds_url(
    migrator: tuple[clients.Migrator, Mock, Mock],
) -> None:
    instance, confluence, _ = migrator
    confluence.get_page_by_id.return_value = {
        "id": 123,
        "title": "Migration guide",
        "body": {"storage": {"value": "<p>Content</p>"}},
        "_links": {"webui": "/spaces/DEMO/pages/123"},
    }

    page = instance.get_page("123")

    confluence.get_page_by_id.assert_called_once_with("123", expand="body.storage,_links")
    assert page.page_id == "123"
    assert page.title == "Migration guide"
    assert page.body == "<p>Content</p>"
    assert page.url == "https://confluence.example.com/spaces/DEMO/pages/123"


def test_get_page_defaults_missing_body_and_link(
    migrator: tuple[clients.Migrator, Mock, Mock],
) -> None:
    instance, confluence, _ = migrator
    confluence.get_page_by_id.return_value = {"id": "7", "title": "Empty"}

    page = instance.get_page("7")

    assert page.body == ""
    assert page.url is None


def test_migrate_page_dry_run_does_not_create_jira_issue(
    migrator: tuple[clients.Migrator, Mock, Mock],
) -> None:
    instance, confluence, jira = migrator
    confluence.get_page_by_id.return_value = {
        "id": "123",
        "title": "Preview",
        "body": {"storage": {"value": "<p>Body</p>"}},
    }

    result = instance.migrate_page("123", "Story", dry_run=True)

    assert result.page_id == "123"
    assert result.issue_key is None
    assert result.summary == "Preview"
    assert result.dry_run is True
    jira.create_issue.assert_not_called()


def test_migrate_page_creates_issue_with_transformed_fields(
    migrator: tuple[clients.Migrator, Mock, Mock],
) -> None:
    instance, confluence, jira = migrator
    confluence.get_page_by_id.return_value = {
        "id": "123",
        "title": "Create me",
        "body": {"storage": {"value": "<p>Body</p>"}},
    }
    jira.create_issue.return_value = SimpleNamespace(key="DEMO-42")

    result = instance.migrate_page("123", "Bug")

    jira.create_issue.assert_called_once_with(
        fields={
            "project": {"key": "DEMO"},
            "summary": "Create me",
            "description": "Body",
            "issuetype": {"name": "Bug"},
        }
    )
    assert result.issue_key == "DEMO-42"
    assert result.dry_run is False
