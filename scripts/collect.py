#!/usr/bin/env python3
"""Collect one day of public activity for a Firehose entry. Prints JSON to stdout.

Sources: public GitHub repos, public Hugging Face models and datasets, the blog RSS feed.
Standard library only. GitHub token: $GH_TOKEN, else `gh auth token`, else anonymous.

Usage: collect.py [--date YYYY-MM-DD] [--tz Asia/Jerusalem]
"""
import argparse, datetime as dt, email.utils, json, os, subprocess, sys
import urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

GH_OWNERS = ["danielrosehill"]
HF_AUTHORS = ["danielrosehill"]
BLOG_FEED = "https://blog.danielrosehill.com/rss.xml"
EXCLUDE_REPOS = {"danielrosehill/Firehose"}  # the digest does not report on itself
MAX_COMMITS = 30  # messages kept per repo; commit_count stays exact up to 100


def token():
    if os.environ.get("GH_TOKEN"):
        return os.environ["GH_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "firehose-author", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse_ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def github(owner, start, end, tok, errors):
    h = {"Accept": "application/vnd.github+json"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    api = "https://api.github.com"
    since, until = (t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") for t in (start, end))
    out, page, done = [], 1, False
    while not done:
        repos = json.loads(fetch(f"{api}/users/{owner}/repos?type=owner&sort=pushed&direction=desc&per_page=100&page={page}", h))
        if not repos:
            break
        for r in repos:
            if not r.get("pushed_at") or parse_ts(r["pushed_at"]) < start:
                done = True  # sorted by push time: everything after this is older
                break
            if r["private"] or r["fork"] or r["full_name"] in EXCLUDE_REPOS:
                continue
            created = start <= parse_ts(r["created_at"]) < end
            commits = []
            try:
                raw = json.loads(fetch(f"{api}/repos/{r['full_name']}/commits?since={since}&until={until}&per_page=100", h))
                commits = [{"message": c["commit"]["message"].split("\n")[0], "url": c["html_url"]} for c in raw]
            except urllib.error.HTTPError as e:
                if e.code != 409:  # 409 = empty repository
                    errors.append(f"commits {r['full_name']}: HTTP {e.code}")
            releases = []
            try:
                raw = json.loads(fetch(f"{api}/repos/{r['full_name']}/releases?per_page=10", h))
                releases = [{"tag": x["tag_name"], "name": x["name"], "url": x["html_url"]} for x in raw
                            if x.get("published_at") and start <= parse_ts(x["published_at"]) < end]
            except urllib.error.HTTPError as e:
                errors.append(f"releases {r['full_name']}: HTTP {e.code}")
            if created or commits or releases:
                out.append({"repo": r["full_name"], "url": r["html_url"], "description": r["description"],
                            "topics": r.get("topics", []), "created_today": created,
                            "commit_count": len(commits), "commits": commits[:MAX_COMMITS], "releases": releases})
        page += 1
    return out


def huggingface(kind, author, start, end):
    # kind: "models" or "datasets". Sorted newest-modified first, so stop at the first older item.
    url = f"https://huggingface.co/api/{kind}?author={urllib.parse.quote(author)}&sort=lastModified&direction=-1&limit=100&full=true"
    base = "https://huggingface.co/" + ("datasets/" if kind == "datasets" else "")
    out = []
    for m in json.loads(fetch(url)):
        if m.get("private") or m.get("gated") not in (False, None):
            continue
        modified = parse_ts(m["lastModified"])
        if modified < start:
            break
        created = parse_ts(m["createdAt"]) if m.get("createdAt") else None
        is_new = bool(created and start <= created < end)
        if modified < end or is_new:
            out.append({"id": m["id"], "url": base + m["id"], "created_today": is_new,
                        "tags": [t for t in m.get("tags", []) if ":" not in t][:8]})
    return out


def blog(start, end):
    out = []
    for item in ET.fromstring(fetch(BLOG_FEED)).iter("item"):
        pub = item.findtext("pubDate")
        if pub and start <= email.utils.parsedate_to_datetime(pub) < end:
            out.append({"title": item.findtext("title"), "url": item.findtext("link"),
                        "summary": (item.findtext("description") or "")[:300]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tz", default="Asia/Jerusalem")
    ap.add_argument("--date", help="YYYY-MM-DD, default today in --tz")
    a = ap.parse_args()
    tz = ZoneInfo(a.tz)
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(tz).date()
    start = dt.datetime.combine(day, dt.time.min, tz)
    end = start + dt.timedelta(days=1)
    errors, result, tok = [], {"date": day.isoformat(), "timezone": a.tz}, token()

    def source(name, fn):
        # A failed source is reported, never silently read as "no activity".
        try:
            return fn()
        except Exception as e:
            errors.append(f"{name}: {e}")
            return []

    result["github"] = [x for o in GH_OWNERS for x in source(f"github {o}", lambda: github(o, start, end, tok, errors))]
    result["hf_models"] = [x for o in HF_AUTHORS for x in source(f"hf models {o}", lambda: huggingface("models", o, start, end))]
    result["hf_datasets"] = [x for o in HF_AUTHORS for x in source(f"hf datasets {o}", lambda: huggingface("datasets", o, start, end))]
    result["blog"] = source("blog", lambda: blog(start, end))
    result["errors"] = errors
    json.dump(result, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
