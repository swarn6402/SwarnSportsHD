"""Offline source and site checks; no backend imports or network access."""

import ast
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent


def check_reference(value: str, source: Path) -> None:
    """Check local HTML/manifest paths without visiting external destinations."""
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return
    path = unquote(parsed.path)
    if path.startswith("/") or "\\" in path:
        raise ValueError(f"{source}: use a relative asset path: {value}")
    target = (ROOT / source.parent / path).resolve()
    if not target.is_relative_to(ROOT) or not target.is_file():
        raise ValueError(f"{source}: missing local file: {value}")


class SiteReferences(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"src", "href"} and value:
                check_reference(value, Path("index.html"))


def check_data(data: dict) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("timestamp"), str):
        raise ValueError("data.json: expected an object with a timestamp string")
    if not isinstance(data.get("links"), list):
        raise ValueError("data.json: expected a links array (an empty array is valid)")
    fields = ("url", "source_channel_name", "message_text")
    for index, link in enumerate(data["links"]):
        if (
            not isinstance(link, dict)
            or any(not isinstance(link.get(field), str) for field in fields)
            or type(link.get("source_channel_id")) is not int
            or "posted_time" not in link
            or not (link["posted_time"] is None or isinstance(link["posted_time"], str))
        ):
            raise ValueError(f"data.json: record {index} does not match the data contract")


def main() -> None:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    paths = {Path(value) for value in tracked.decode("utf-8").split("\0") if value}
    paths.add(Path(__file__).resolve().relative_to(ROOT))
    python_count = json_count = 0
    for path in sorted(paths):
        if path.suffix == ".py":
            ast.parse((ROOT / path).read_text(encoding="utf-8-sig"), filename=str(path))
            python_count += 1
        elif path.suffix in {".json", ".webmanifest"}:
            data = json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
            if path == Path("data.json"):
                check_data(data)
            elif path == Path("site.webmanifest"):
                for icon in data["icons"]:
                    check_reference(icon["src"], path)
            json_count += 1

    parser = SiteReferences()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    parser.close()
    print(f"Passed: {python_count} Python files, {json_count} JSON/manifest files, "
          "data contract, and local HTML/manifest references.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, subprocess.CalledProcessError) as exc:
        print(f"Check failed: {exc}", file=sys.stderr)
        sys.exit(1)
