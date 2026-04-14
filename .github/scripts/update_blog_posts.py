"""Scrape latest posts from 637techlife blog and inject into README."""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

BLOG_URL = "https://a637i.top/"
MAX_POSTS = 5
README = Path(__file__).resolve().parents[2] / "README.md"
START_MARK = "<!-- BLOG-POST-LIST:START -->"
END_MARK = "<!-- BLOG-POST-LIST:END -->"

POST_RE = re.compile(
    r'<h1 class="index-header">\s*<a href="([^"]+)"[^>]*>\s*([^<]+?)\s*</a>',
    re.DOTALL,
)


def fetch_posts() -> list[tuple[str, str]]:
    req = urllib.request.Request(BLOG_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    matches = POST_RE.findall(html)
    seen = set()
    posts = []
    for href, title in matches:
        key = (href, title.strip())
        if key in seen:
            continue
        seen.add(key)
        full = href if href.startswith("http") else BLOG_URL.rstrip("/") + href
        posts.append((title.strip(), full))
        if len(posts) >= MAX_POSTS:
            break
    return posts


def render(posts: list[tuple[str, str]]) -> str:
    if not posts:
        return "- _No posts found — check scraper or blog layout._"
    return "\n".join(f"- [{title}]({url})" for title, url in posts)


def update_readme(block: str) -> bool:
    original = README.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"({re.escape(START_MARK)})(.*?)({re.escape(END_MARK)})",
        re.DOTALL,
    )
    if not pattern.search(original):
        print("markers not found in README", file=sys.stderr)
        return False
    updated = pattern.sub(rf"\1\n{block}\n\3", original)
    if updated == original:
        print("no change")
        return False
    README.write_text(updated, encoding="utf-8")
    print("README updated")
    return True


def main() -> int:
    posts = fetch_posts()
    print(f"fetched {len(posts)} posts")
    update_readme(render(posts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
