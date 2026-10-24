"""Offline MkDocs navigation, local-link and package-CLI contract verification."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HEAD = re.compile(r"^#{1,6}\s+", re.MULTILINE)
REQUIRED_SCRIPTS = {
    "sensorlab", "degradesim", "fusionlab", "bench-rgbt", "edgelab",
    "arc-rgbt-e00", "arc-rgbt-e01", "arc-rgbt-e02",
    "arc-rgbt-sync", "arc-rgbt-register",
}


def nav_paths(value: object) -> list[str]:
    """Flatten label dictionaries and nested nav lists into Markdown paths."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [p for item in value for p in nav_paths(item)]
    if isinstance(value, dict):
        return [p for item in value.values() for p in nav_paths(item)]
    raise ValueError("Invalid MkDocs navigation entry")


def check(root: Path = ROOT) -> tuple[int, int]:
    """Raise ValueError on broken docs; return count of pages and local links."""
    docs = root / "docs"
    config = yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("docs_dir", "docs") != "docs":
        raise ValueError("Docs must be rooted at docs/")
    nav = nav_paths(config["nav"])
    declared = set(nav)
    existing = {p.relative_to(docs).as_posix() for p in docs.rglob("*.md")}
    if len(nav) != len(declared):
        raise ValueError("Duplicate MkDocs nav item")
    if declared != existing:
        raise ValueError(
            f"Navigation mismatch: omitted={sorted(existing - declared)} "
            f"missing={sorted(declared - existing)}"
        )
    links = 0
    for rel in sorted(existing):
        path = docs / rel
        body = path.read_text(encoding="utf-8")
        if not HEAD.search(body):
            raise ValueError(f"Missing Markdown heading: {rel}")
        if body.count(chr(96) * 3) % 2:
            raise ValueError(f"Unbalanced code fences: {rel}")
        for raw in LINK.findall(body):
            target = unquote(raw.strip("<>"))
            url = urlsplit(target)
            if url.scheme or url.netloc or target.startswith("#"):
                continue
            if url.path.startswith("/"):
                raise ValueError(f"Absolute local link: {rel} -> {target}")
            resolved = (path.parent / url.path).resolve()
            if not resolved.is_relative_to(docs.resolve()) or not resolved.is_file():
                raise ValueError(f"Broken documentation link: {rel} -> {target}")
            links += 1
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = project["project"]["scripts"]
    if not isinstance(scripts, dict) or not REQUIRED_SCRIPTS.issubset(scripts):
        raise ValueError("Missing expected CLI entry points in pyproject.toml")
    if "docs" not in project["project"]["optional-dependencies"]:
        raise ValueError("Missing docs dependency extra")
    cli_doc = (docs / "reference" / "cli.md").read_text(encoding="utf-8")
    not_documented = sorted(
        name for name in scripts
        if f"{chr(96)}{name}{chr(96)}" not in cli_doc
    )
    if not_documented:
        raise ValueError(f"Undocumented CLI entry points: {not_documented}")
    return len(existing), links


def main() -> None:
    try:
        pages, links = check()
    except (OSError, KeyError, ValueError, TypeError) as exc:
        sys.exit(f"DOCS_CHECK=FAIL: {exc}")
    print(f"DOCS_CHECK=PASS pages={pages} local_links={links}")


if __name__ == "__main__":
    main()
