from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    confluence_url: str
    confluence_username: str
    confluence_api_token: str
    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_project_key: str

    @classmethod
    def from_env(cls) -> Settings:
        names = (
            "CONFLUENCE_URL",
            "CONFLUENCE_USERNAME",
            "CONFLUENCE_API_TOKEN",
            "JIRA_URL",
            "JIRA_USERNAME",
            "JIRA_API_TOKEN",
            "JIRA_PROJECT_KEY",
        )
        values = {name: os.getenv(name, "").strip() for name in names}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return cls(**{name.lower(): value for name, value in values.items()})
