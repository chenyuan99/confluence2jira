from bs4 import BeautifulSoup

from confluence2jira.models import ConfluencePage


def storage_html_to_text(body: str) -> str:
    soup = BeautifulSoup(body, "html.parser")
    for break_tag in soup.find_all("br"):
        break_tag.replace_with("\n")
    return soup.get_text("\n", strip=True)


def issue_fields(page: ConfluencePage, project_key: str, issue_type: str) -> dict[str, object]:
    description = storage_html_to_text(page.body)
    if page.url:
        description = f"Source: {page.url}\n\n{description}"
    return {
        "project": {"key": project_key},
        "summary": page.title[:255],
        "description": description,
        "issuetype": {"name": issue_type},
    }
