"""Refuse deployment when a generated page links to a missing local file."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.missing_alt = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img" and "alt" not in attrs:
            self.missing_alt += 1
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def check(root):
    root = Path(root).resolve()
    errors = []
    pages = list(root.rglob("*.html"))
    if not pages:
        return ["No generated HTML pages"]
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        if parser.missing_alt:
            errors.append(f"{page.relative_to(root)}: image missing alt attribute")
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            target = (root / path.lstrip("/") if path.startswith("/") else page.parent / path).resolve()
            if not target.is_relative_to(root) or not (target.is_file() or (target / "index.html").is_file()):
                errors.append(f"{page.relative_to(root)}: missing local target {url.path}")
    return errors


if __name__ == "__main__":
    failures = check(sys.argv[1] if len(sys.argv) > 1 else "dist")
    for failure in failures:
        print(failure, file=sys.stderr)
    print(f"Site link/image checks: {len(failures)} errors")
    raise SystemExit(bool(failures))
