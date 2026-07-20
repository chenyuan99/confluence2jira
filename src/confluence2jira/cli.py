from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from confluence2jira.clients import Migrator
from confluence2jira.config import Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate a Confluence page to a Jira issue")
    parser.add_argument("page_id", help="Confluence page ID")
    parser.add_argument("--issue-type", default="Task", help="Jira issue type (default: Task)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Fetch and transform without creating"
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        result = Migrator(Settings.from_env()).migrate_page(
            args.page_id, args.issue_type, dry_run=args.dry_run
        )
    except (KeyError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(json.dumps(asdict(result), indent=2))
