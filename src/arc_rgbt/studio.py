"""Launch the fully offline, self-contained RGB–thermal browser studio."""

from __future__ import annotations

import argparse
import webbrowser
from importlib import resources
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Open the local RGB–thermal studio. No server or uploads."
    )
    parser.add_argument(
        "--no-open", action="store_true",
        help="Print local studio path without opening a browser",
    )
    args = parser.parse_args(argv)
    resource = resources.files("arc_rgbt").joinpath("studio.html")
    path = Path(str(resource)).resolve()
    if not path.is_file():
        parser.exit(1, "Studio HTML resource missing; reinstall arc-rgbt\n")
    print(f"RGB–Thermal Studio: {path}")
    if args.no_open:
        return
    if not webbrowser.open(path.as_uri(), new=2):
        print("Browser could not be launched automatically. Open the file above manually.")


if __name__ == "__main__":
    main()
