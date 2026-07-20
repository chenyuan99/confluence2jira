import pytest

from confluence2jira.config import Settings


ENVIRONMENT = {
    "CONFLUENCE_URL": " https://confluence.example.com ",
    "CONFLUENCE_USERNAME": " confluence-user ",
    "CONFLUENCE_API_TOKEN": " confluence-token ",
    "JIRA_URL": " https://jira.example.com ",
    "JIRA_USERNAME": " jira-user ",
    "JIRA_API_TOKEN": " jira-token ",
    "JIRA_PROJECT_KEY": " DEMO ",
}


def test_settings_loads_and_strips_environment_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name, value in ENVIRONMENT.items():
        monkeypatch.setenv(name, value)

    settings = Settings.from_env()

    assert settings == Settings(
        confluence_url="https://confluence.example.com",
        confluence_username="confluence-user",
        confluence_api_token="confluence-token",
        jira_url="https://jira.example.com",
        jira_username="jira-user",
        jira_api_token="jira-token",
        jira_project_key="DEMO",
    )


def test_settings_reports_all_missing_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValueError, match="CONFLUENCE_URL.*JIRA_PROJECT_KEY"):
        Settings.from_env()


def test_settings_treats_whitespace_only_value_as_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name, value in ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("JIRA_PROJECT_KEY", "   ")

    with pytest.raises(ValueError, match=r"Missing required environment variables: JIRA_PROJECT_KEY"):
        Settings.from_env()
