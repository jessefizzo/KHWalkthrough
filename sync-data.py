#!/usr/bin/env python3
"""Re-embed kh-data.json and kh-enemies.json into index.html.

index.html is self-contained so it can be opened straight off the filesystem —
the objective data lives in its <script id="khdata"> block. Edit kh-data.json,
then run this to push the change into the page.

    python3 sync-data.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
DATA = HERE / "kh-data.json"
ENEMIES = HERE / "kh-enemies.json"
PAGE = HERE / "index.html"

CLOSE = "</script>"
BLOCKS = [
    ('<script id="khdata" type="application/json">', DATA),
    ('<script id="khenemies" type="application/json">', ENEMIES),
]


def main() -> int:
    html = PAGE.read_text(encoding="utf-8")
    changed = []
    for opener, path in BLOCKS:
        if not path.exists():
            print(f"{path.name} is missing — skipped", file=sys.stderr)
            continue
        raw = path.read_text(encoding="utf-8")
        try:
            json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"{path.name} is not valid JSON: {e}", file=sys.stderr)
            return 1
        if "</script" in raw.lower():
            print(f"{path.name} contains '</script' and would close the tag early", file=sys.stderr)
            return 1
        start = html.find(opener)
        if start == -1:
            print(f"could not find the {path.name} block in index.html", file=sys.stderr)
            return 1
        body = start + len(opener)
        end = html.find(CLOSE, body)
        if end == -1:
            print(f"{path.name} block is not closed", file=sys.stderr)
            return 1
        if html[body:end] != raw:
            html = html[:body] + raw + html[end:]
            changed.append(path.name)

    if not changed:
        print("index.html already matches the data files — nothing to do")
        return 0
    PAGE.write_text(html, encoding="utf-8")
    print("embedded " + ", ".join(changed) + " into index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
