#!/usr/bin/env python3
"""Check generated HTML for deterministic accessibility regressions."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path

GENERIC_ALT_TEXT = {"image", "photo", "picture"}


class AccessibilityParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__()
        self.source = source
        self.errors: list[str] = []
        self.anchor_depth = 0

    def add_error(self, message: str) -> None:
        line, column = self.getpos()
        self.errors.append(f"{self.source}:{line}:{column + 1}: {message}")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)

        if tag == "a":
            if self.anchor_depth:
                self.add_error("nested links are not valid or keyboard-accessible")
            self.anchor_depth += 1

        if tag != "img":
            return

        alt = attributes.get("alt")
        is_decorative = attributes.get("aria-hidden") == "true" or attributes.get("role") in {"none", "presentation"}
        if alt is None:
            self.add_error("image is missing an alt attribute")
        elif not alt.strip() and not is_decorative:
            self.add_error("informative image has empty alt text")
        elif alt.strip().lower() in GENERIC_ALT_TEXT:
            self.add_error(f'image has non-descriptive alt text: "{alt}"')

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag == "a":
            self.anchor_depth -= 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.anchor_depth:
            self.anchor_depth -= 1


def check_site(site_dir: Path) -> list[str]:
    errors: list[str] = []
    for html_file in sorted(site_dir.rglob("*.html")):
        parser = AccessibilityParser(html_file)
        parser.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        errors.extend(parser.errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_dir", nargs="?", default="_site", type=Path)
    args = parser.parse_args()

    errors = check_site(args.site_dir)
    if errors:
        print("\n".join(errors))
        print(f"\nFound {len(errors)} HTML accessibility error(s).")
        return 1

    print(f"Accessibility checks passed for {args.site_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
