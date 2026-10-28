"""Quality checks for the static site: run `python scripts/check_site.py` from the repository root.

Every page must parse, declare a language and a title, show the version in VERSION, link only to files and anchors that exist,
and the Play Console's "delete your data" anchor (en.html#delete) must stay in place.
"""
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "en.html", "pt-BR.html"]
errors: list[str] = []


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.language = ""
        self.title = ""
        self.in_title = False
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.version_texts: list[str] = []
        self._in_version = False

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag == "html":
            self.language = values.get("lang") or ""
        if tag == "title":
            self.in_title = True
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if "site-version" in (values.get("class") or ""):
            self._in_version = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "p":
            self._in_version = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._in_version:
            self.version_texts.append(data)


version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    errors.append(f"VERSION must look like 1.2.3, found {version!r}")

parsed: dict[str, PageParser] = {}
for name in PAGES:
    path = ROOT / name
    if not path.is_file():
        errors.append(f"{name} is missing")
        continue
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parsed[name] = parser
    if not parser.language:
        errors.append(f"{name}: <html> has no lang")
    if not parser.title.strip():
        errors.append(f"{name}: no <title>")
    if not any(version in text for text in parser.version_texts):
        errors.append(f"{name}: no 'site-version' paragraph showing {version}")

for name, parser in parsed.items():
    for link in parser.links:
        if re.match(r"^(https?:|mailto:)", link):
            continue
        target, _, anchor = link.partition("#")
        target_name = target or name
        if not (ROOT / target_name).is_file():
            errors.append(f"{name}: link {link} points to a missing file")
        elif anchor and anchor not in parsed.get(target_name, PageParser()).ids:
            errors.append(f"{name}: link {link} points to a missing anchor")

if "delete" not in parsed.get("en.html", PageParser()).ids:
    errors.append("en.html must keep the id 'delete' (the Play Console data deletion URL)")
ads = ROOT / "app-ads.txt"
if not ads.is_file() or not re.search(r"^google\.com, pub-\d{16}, DIRECT, \w+$", ads.read_text(encoding="utf-8"), re.M):
    errors.append("app-ads.txt must keep the AdMob line")
cname = ROOT / "CNAME"
if not cname.is_file() or not cname.read_text(encoding="utf-8").strip():
    errors.append("CNAME is missing or empty")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Site {version} is fine: {', '.join(PAGES)}")
