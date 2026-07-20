from confluence2jira.models import ConfluencePage
from confluence2jira.transform import issue_fields, storage_html_to_text


def test_storage_html_to_text() -> None:
    assert storage_html_to_text("<p>Hello <strong>world</strong></p><p>Next</p>") == (
        "Hello\nworld\nNext"
    )


def test_storage_html_to_text_handles_breaks_and_empty_content() -> None:
    assert storage_html_to_text("<p>First<br>Second</p>") == "First\nSecond"
    assert storage_html_to_text("") == ""


def test_issue_fields_include_source_and_truncate_summary() -> None:
    page = ConfluencePage("123", "x" * 300, "<p>Body</p>", "https://example/page/123")

    fields = issue_fields(page, "DEMO", "Story")

    assert fields["project"] == {"key": "DEMO"}
    assert fields["issuetype"] == {"name": "Story"}
    assert len(fields["summary"]) == 255
    assert fields["description"] == "Source: https://example/page/123\n\nBody"


def test_issue_fields_omits_source_prefix_when_page_has_no_url() -> None:
    page = ConfluencePage("123", "Title", "<p>Body</p>")

    fields = issue_fields(page, "DEMO", "Task")

    assert fields == {
        "project": {"key": "DEMO"},
        "summary": "Title",
        "description": "Body",
        "issuetype": {"name": "Task"},
    }
