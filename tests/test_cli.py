import json
from unittest.mock import Mock

import pytest

import confluence2jira.cli as cli
from confluence2jira.models import MigrationResult


def test_main_prints_migration_result(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    settings = object()
    migrator = Mock()
    migrator.migrate_page.return_value = MigrationResult(
        page_id="123", issue_key=None, summary="Preview", dry_run=True
    )
    settings_loader = Mock(return_value=settings)
    migrator_constructor = Mock(return_value=migrator)
    monkeypatch.setattr(cli.Settings, "from_env", settings_loader)
    monkeypatch.setattr(cli, "Migrator", migrator_constructor)
    monkeypatch.setattr(cli.sys, "argv", ["confluence2jira", "123", "--dry-run"])

    cli.main()

    settings_loader.assert_called_once_with()
    migrator_constructor.assert_called_once_with(settings)
    migrator.migrate_page.assert_called_once_with("123", "Task", dry_run=True)
    assert json.loads(capsys.readouterr().out) == {
        "page_id": "123",
        "issue_key": None,
        "summary": "Preview",
        "dry_run": True,
    }


def test_main_passes_custom_issue_type(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    migrator = Mock()
    migrator.migrate_page.return_value = MigrationResult("9", "DEMO-1", "Bug")
    monkeypatch.setattr(cli.Settings, "from_env", Mock(return_value=object()))
    monkeypatch.setattr(cli, "Migrator", Mock(return_value=migrator))
    monkeypatch.setattr(cli.sys, "argv", ["confluence2jira", "9", "--issue-type", "Bug"])

    cli.main()

    migrator.migrate_page.assert_called_once_with("9", "Bug", dry_run=False)
    assert json.loads(capsys.readouterr().out)["issue_key"] == "DEMO-1"


@pytest.mark.parametrize("error", [KeyError("id"), RuntimeError("offline"), ValueError("bad")])
def test_main_reports_expected_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: Exception,
) -> None:
    migrator = Mock()
    migrator.migrate_page.side_effect = error
    monkeypatch.setattr(cli.Settings, "from_env", Mock(return_value=object()))
    monkeypatch.setattr(cli, "Migrator", Mock(return_value=migrator))
    monkeypatch.setattr(cli.sys, "argv", ["confluence2jira", "123"])

    with pytest.raises(SystemExit) as raised:
        cli.main()

    assert raised.value.code == 2
    assert capsys.readouterr().err.startswith("error: ")
