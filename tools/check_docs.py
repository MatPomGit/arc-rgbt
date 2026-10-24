"""Check MkDocs navigation, Markdown links and source-backed CLI references offline."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")
HEAD = re.compile(r"^#{1,6}\s+", re.MULTILINE)


def nav_paths(value: object) -> list[str]:
    """Extract paths from the nested MkDocs navigation definition."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [path for item in value for path in nav_paths(item)]
    if isinstance(value, dict):
        return [path for item in value.values() for path in nav_paths(item)]
    raise ValueError("Invalid MkDocs nav entry")


def check() -> tuple[int, int]:
    """Raise a descriptive error for a broken documentation contract."""
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("docs_dir", "docs") != "docs":
        raise ValueError("Docs must be rooted at docs/")
    paths = nav_paths(config["nav"])
    declared = set(paths)
    existing = {p.relative_to(DOCS).as_posix() for p in DOCS.rglob("*.md")}
    if len(paths) != len(declared):
        raise ValueError("Duplicate MkDocs nav item")
    if declared != existing:
        raise ValueError(f"Navigation mismatch: missing={sorted(existing-declared)} "
                         f"nonexistent={sorted(declared-existing)}")
    count = 0
    for rel in sorted(existing):
        path = DOCS / rel
        body = path.read_text(encoding="utf-8")
        if not HEAD.search(body):
            raise ValueError(f"Missing heading: {rel}")
        if body.count("```") % 2:
            raise ValueError(f"Unbalanced fenced code blocks: {rel}")
        for raw in LINK.findall(body):
            target = unquote(raw.strip("<>"))
            url = urlsplit(target)
            if url.scheme or url.netloc or target.startswith("#"):
                continue
            if url.path.startswith("/"):
                raise ValueError(f"Absolute local link: {rel} -> {target}")
            resolved = (path.parent / url.path).resolve()
            if not resolved.is_relative_to(DOCS.resolve()) or not resolved.is_file():
                raise ValueError(f"Broken documentation link: {rel} -> {target}")
            count += 1
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    required = {"sensorlab", "degradesim", "fusionlab", "bench-rgbt",
                "edgelab", "arc-rgbt-e00", "arc-rgbt-sync", "arc-rgbt-register"}
    if not required.issubset(project["project"]["scripts"]):
        raise ValueError("Documented CLI entry points differ from package metadata")
    if "docs" not in project["project"]["optional-dependencies"]:
        raise ValueError("Missing docs dependency extra")
    return len(existing), count


def main() -> None:
    try:
        pages, links = check()
    except (OSError, KeyError, ValueError, TypeError) as exc:
        sys.exit(f"DOCS_CHECK=FAIL: {exc}")
    print(f"DOCS_CHECK=PASS pages={pages} local_links={links}")


if __name__ == "__main__":
    main()
