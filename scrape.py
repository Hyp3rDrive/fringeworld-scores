#!/usr/bin/env python3
"""Copy the Fringe World itch.io comments into posts.json.

Run by .github/workflows/scrape.yml every ~15 minutes. Web builds of the game can't read itch.io
pages (no CORS headers), but they can read raw files from this public repo, so this keeps a copy.

It only copies posts (id, author, text). The game itself checks the signed scores, filters and
ranks them, so nothing here needs keys or can make a score count that shouldn't.
Keep the parsing in step with Leaderboard.parse_posts() in the game (scripts/leaderboard.gd).
"""
import html
import json
import re
import sys
import urllib.request

COMMENTS_URL = "https://hyp3rdrive.itch.io/fringe-world/comments"
MAX_PAGES = 10
OUT = "posts.json"
USER_AGENT = "Mozilla/5.0 (compatible; FringeWorldScoresMirror/1.0; +https://github.com/Hyp3rDrive/fringeworld-scores)"

POST_RE = re.compile(
    r'class="community_post[^"]*" id="post-(\d+)".*?<span class="post_author"><a[^>]*>(.*?)</a></span>'
    r'.*?<div[^>]*class="post_body[^"]*"[^>]*>(.*?)</div>', re.S)
NEXT_RE = re.compile(r'href="([^"]*/comments\?(?:before|page)=[^"]*)"[^>]*>[^<]*(?:Next|Older|More)')


def html_to_text(h: str) -> str:
    t = re.sub(r"<br\s*/?>", "\n", h)
    t = t.replace("</p>", "\n")
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t)


def parse_posts(page: str) -> list:
    return [{"id": int(m.group(1)), "user": html_to_text(m.group(2)).strip(), "text": html_to_text(m.group(3))}
            for m in POST_RE.finditer(page)]


def next_page_url(page: str) -> str:
    m = NEXT_RE.search(page)
    if not m:
        return ""
    url = m.group(1).replace("&amp;", "&")
    return url if url.startswith("http") else "https://hyp3rdrive.itch.io" + url


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main() -> int:
    posts, seen, url = {}, set(), COMMENTS_URL
    for _ in range(MAX_PAGES):
        if not url or url in seen:
            break
        seen.add(url)
        page = fetch(url)
        for p in parse_posts(page):
            posts[p["id"]] = p
        url = next_page_url(page)
    ordered = sorted(posts.values(), key=lambda p: p["id"])
    try:
        old = json.load(open(OUT)).get("posts")
    except (OSError, ValueError):
        old = None
    if old == ordered:
        print(f"No change ({len(ordered)} posts).")
        return 0
    with open(OUT, "w") as f:
        json.dump({"source": COMMENTS_URL, "posts": ordered}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {len(ordered)} posts.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:  # parse a saved page instead of fetching: python3 scrape.py page.html
        print(json.dumps(parse_posts(open(sys.argv[1]).read()), indent=1))
        sys.exit(0)
    sys.exit(main())
